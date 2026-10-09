import arc_agi
from arc_agi import OperationMode
from arcengine import GameAction

arc=arc_agi.Arcade(operation_mode=OperationMode.NORMAL)

# Visible rows:
# top:    9,14,11,15 at x 20,27,34,41 y3
# bottom:14,15, 9,11 at x 19,27,35,43 y58
top_by_color={9:(20,3),14:(27,3),11:(34,3),15:(41,3)}
bot_by_color={14:(19,58),15:(27,58),9:(35,58),11:(43,58)}
top_order=[9,14,11,15]
bot_order=[14,15,9,11]

cases=[
 ("bottom_as_vocab_top_as_target",[bot_by_color[c] for c in top_order]),
 ("top_as_vocab_bottom_as_target",[top_by_color[c] for c in bot_order]),
 ("top_direct",[top_by_color[c] for c in top_order]),
 ("bottom_direct",[bot_by_color[c] for c in bot_order]),
]
for name,steps in cases:
    env=arc.make("sb26")
    print("\nCASE",name,steps)
    for i,(x,y) in enumerate(steps,1):
        a=GameAction.ACTION6; a.set_data({"x":x,"y":y})
        out=env.step(a,data=a.action_data.model_dump(),reasoning={"probe":name,"phase":"select","i":i})
        out=env.step(GameAction.ACTION5,data={},reasoning={"probe":name,"phase":"submit","i":i})
        print(i,"levels",out.levels_completed,"state",out.state)
        if out.levels_completed>0 or "WIN" in str(out.state) or "GAME_OVER" in str(out.state):
            break
