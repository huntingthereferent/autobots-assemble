from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from runtime import Handoff, HandoffRuntime
from systems.calendar import CalendarEvent, CalendarStore
from systems.day_to_day import DayToDayStore, Reminder, attention_projection


NOW=datetime.fromisoformat("2026-10-05T09:30:00-05:00")


class DayToDayTests(unittest.TestCase):
    def test_calendar_is_time_truth_not_automatic_task(self):
        calendar=CalendarStore()
        event=calendar.add(CalendarEvent.create(
            "School block",referent="school / day",
            participants=("james",),starts_at="2026-10-05T09:30:00-05:00"))
        self.assertEqual(calendar.events(),(event,))
        self.assertEqual(len(calendar.events_for("james",now=NOW)),1)
        self.assertEqual(len(calendar.events_for("other",now=NOW)),0)

    def test_calendar_preserves_words_movement_anchor(self):
        calendar=CalendarStore()
        event=calendar.add(CalendarEvent.create(
            "Follow up",referent="conversation / repo",
            participants=("james",),movement_anchor="reopen",
            starts_at="2026-10-05T09:30:00-05:00"))
        self.assertEqual(event.movement_anchor,"REOPEN")
        self.assertEqual(calendar.events_for("james",now=NOW)[0].movement_anchor,"REOPEN")

    def test_attention_combines_live_work_reminder_and_calendar_per_person(self):
        runtime=HandoffRuntime()
        mine=Handoff(handoff_id="mine",referent="repo",from_actor="x",to_actor="james",
                     required_relation="review",metadata={"title":"Review repo"})
        other=Handoff(handoff_id="other",referent="school",from_actor="x",to_actor="other",
                      required_relation="learn",metadata={"title":"Other work"})
        runtime.submit(mine); runtime.submit(other)

        reminder=Reminder.create("Check the day",actor_id="james",referent="current day")
        event=CalendarEvent.create("Appointment",referent="appointment",
                                   participants=("james",),starts_at="2026-10-05T14:00:00-05:00")
        projection=attention_projection(
            actor_id="james",now=NOW,
            handoffs=[(mine,runtime.state("mine")),(other,runtime.state("other"))],
            reminders=(reminder,),calendar_events=(event,))
        self.assertEqual([x["title"] for x in projection["tasks"]],["Review repo"])
        self.assertEqual([x["text"] for x in projection["reminders"]],["Check the day"])
        self.assertEqual([x["title"] for x in projection["calendar"]],["Appointment"])

    def test_acknowledged_reminder_leaves_today_attention(self):
        store=DayToDayStore()
        reminder=store.add_reminder(Reminder.create(
            "Morning check",actor_id="james",referent="day",cadence="daily"))
        self.assertEqual(store.due_reminders("james",now=NOW),(reminder,))
        store.acknowledge(reminder.reminder_id,local_date="2026-10-05")
        self.assertEqual(store.due_reminders("james",now=NOW),())

    def test_calendar_and_reminders_recover_from_append_only_state(self):
        with TemporaryDirectory() as tmp:
            cpath=Path(tmp)/"calendar.jsonl"; rpath=Path(tmp)/"reminders.jsonl"
            cal=CalendarStore(cpath); day=DayToDayStore(rpath)
            cal.add(CalendarEvent.create("Deadline",referent="work",participants=("james",),
                                         due_at="2026-10-05T17:00:00-05:00"))
            day.add_reminder(Reminder.create("Check deadline",actor_id="james",referent="work"))
            self.assertEqual(len(CalendarStore(cpath).events()),1)
            self.assertEqual(len(DayToDayStore(rpath).reminders()),1)


if __name__=="__main__":
    unittest.main()
