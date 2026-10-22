"""Source-pinned author Bgee PostgreSQL ZIP: original SQL structure only.

We accept *one* immutable owner-repo ZIP, inspect valid plaintext SQL safely,
count explicit original database rows and source-qualified expression calls.
No materialization, SQL execution, hardcoded gene identities, patient records
or invented inference score. Archive release commit and Git blob identity are
verified by the GitHub workflow before this parser is called.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256,sha1
import json
from pathlib import Path
import re
from zipfile import ZipFile,BadZipFile

from . import nih_p2_author_genex_bgee_ro_mapping_gate as bridge

SCHEMA="nih-p2-original-bgee-postgresql-archive-structure-v1"
MAX_ARCHIVE_BYTES=30_000_000
MAX_MEMBER_BYTES=35_000_000
MAX_TOTAL_DECOMPRESSED=50_000_000
MAX_MEMBERS=16
TABLE_COPY=re.compile(r'^COPY\s+([^ (]+)\s*\(([^)]*)\)\s+FROM\s+stdin;\s*$',re.I)
INSERT=re.compile(r'^INSERT\s+INTO\s+([^ (]+)',re.I)


def canonical_table(ref):
    return ref.rsplit(".",1)[-1].replace('"',"").lower()


def sql_census(raw):
    """Walk a finite owner original SQL dump; never executes the SQL."""
    data=raw.decode("utf8","strict")
    lines=data.splitlines()
    counts=Counter()
    positive=Counter()
    copy_sections=[]
    active=None
    headers={}
    for line in lines:
        if active is not None:
            if line=="\.":
                active=None
                continue
            counts[active]+=1
            columns=headers[active]
            if active=="globalexpression" and "calltype" in columns:
                values=line.split(chr(9))
                idx=columns.index("calltype")
                if len(values)!=len(columns):
                    raise ValueError("original COPY row/column arity differs")
                positive[values[idx]]+=1
            continue
        m=TABLE_COPY.match(line)
        if m:
            active=canonical_table(m.group(1))
            cols=tuple(x.strip().replace('"',"").lower() for x in m.group(2).split(","))
            if not cols or any(not x for x in cols):
                raise ValueError("original COPY header columns malformed")
            if active in headers and headers[active]!=cols:
                raise ValueError("same source table COPY has divergent schema")
            headers[active]=cols
            copy_sections.append({"table":active,"column_count":len(cols)})
            continue
        m=INSERT.match(line)
        if m:
            counts["SQL_INSERT_STATEMENT_"+canonical_table(m.group(1))]+=1
    if active is not None:
        raise ValueError("source SQL COPY section not closed")
    return {
       "sql_plaintext_bytes":len(raw),
       "source_sql_line_count":len(lines),
       "recognized_COPY_sections":len(copy_sections),
       "original_table_row_or_INSERT_statement_counts":dict(sorted(counts.items())),
       "original_source_globalexpression_calltypes":dict(sorted(positive.items())),
       "recognized_table_column_counts":{k:len(v) for k,v in sorted(headers.items())},
       "recognized_table_column_names":{k:list(v) for k,v in sorted(headers.items())},
       "original_database_rows_executed_or_materialized":False,
       "frozen_author_mapping_join_executed":False,
       "source_rows_contain_patient_identifiers_claimed":False,
       "schema_is_partially_inspectable":bool(copy_sections),
    }


def examine_archive(path, *, expected_git_blob=None):
    data=Path(path).read_bytes()
    if not 100<=len(data)<=MAX_ARCHIVE_BYTES:
        raise ValueError("original data archive unreasonable compressed size")
    blob=bridge.git_blob(data)
    if expected_git_blob is not None and blob!=expected_git_blob:
        raise ValueError("whole owner Git blob preflight changed")
    out={
        "schema":SCHEMA,
        "source_archive_owner":bridge.OWNER,
        "source_archive_commit":bridge.COMMIT,
        "source_archive_relative_path":"data/postgresql.zip",
        "complete_original_source_zip_sha256":sha256(data).hexdigest(),
        "complete_original_source_git_blob_sha1":blob,
        "git_blob_already_cross_checked_with_original_owner_api":expected_git_blob is not None,
        "compressed_archive_bytes":len(data),
        "original_archive_members":[],
        "original_sql_censuses":[],
        "original_bgee_join_executed":False,
        "original_ontology_reasoning_performed_on_data":False,
        "original_W13_modified":False,
        "official_NIH_benchmark":False,
    }
    try:
        with ZipFile(path) as z:
            selected=[x for x in z.infolist() if not x.is_dir()]
            if not selected or len(selected)>MAX_MEMBERS:
                raise ValueError("source ZIP unexpectedly many member files")
            if sum(x.file_size for x in selected)>MAX_TOTAL_DECOMPRESSED:
                raise ValueError("source ZIP decompress bomb bound")
            for info in selected:
                name=info.filename
                if name.startswith("/") or ".." in name.split("/") or chr(92) in name:
                    raise ValueError("noncanonical original ZIP member path")
                if info.file_size>MAX_MEMBER_BYTES:
                    raise ValueError("source single member size above bound")
                buf=z.read(info)
                if len(buf)!=info.file_size:
                    raise ValueError("compressed original ZIP member size mismatch")
                member={
                    "original_zip_member":name,
                    "source_member_uncompressed_bytes":len(buf),
                    "source_member_sha256":sha256(buf).hexdigest(),
                }
                looks_sql=buf[:100].lower().find(b"postgresql")>=0 or b"COPY " in buf[:500000] or b"CREATE TABLE" in buf[:500000]
                if looks_sql:
                    stats=sql_census(buf)
                    stats["original_zip_member"]=name
                    out["original_sql_censuses"].append(stats)
                    member["SQL_source_content_recognized"]=True
                else:
                    member["SQL_source_content_recognized"]=False
                out["original_archive_members"].append(member)
    except BadZipFile as e:
        raise ValueError("authenticated author archive is not a usable ZIP") from e
    out["at_least_one_SQL_content_member_recognized"]=bool(out["original_sql_censuses"])
    out["source_measured_expression_rows"]=sum(
        sum(n for t,n in stats["original_source_globalexpression_calltypes"].items()
            if t.upper()=="EXPRESSED")
        for stats in out["original_sql_censuses"])
    out["database_original_positive_expression_calls_measured"] = any(
        bool(stats["original_source_globalexpression_calltypes"])
        for stats in out["original_sql_censuses"])
    out["positives_are_not_materialized_gene_anatomy_edges"]=True
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--archive",required=True,type=Path)
    parser.add_argument("--expected-blob",required=True)
    parser.add_argument("--output",required=True,type=Path)
    opts=parser.parse_args()
    result=examine_archive(opts.archive,expected_git_blob=opts.expected_blob)
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(result,sort_keys=True,indent=2)+chr(10))
    print(json.dumps({
       "original_archive_git_blob_verified":result["git_blob_already_cross_checked_with_original_owner_api"],
       "source_SQL_members":len(result["original_sql_censuses"]),
       "source_expression_calls":result["source_measured_expression_rows"],
       "source_table_schemas":[r["recognized_table_column_names"] for r in result["original_sql_censuses"]],
       "source_table_row_counts":[r["original_table_row_or_INSERT_statement_counts"] for r in result["original_sql_censuses"]],
       "original_join_materialized":False,
       "NIH_completed":False},sort_keys=True))


if __name__=="__main__":
    main()
