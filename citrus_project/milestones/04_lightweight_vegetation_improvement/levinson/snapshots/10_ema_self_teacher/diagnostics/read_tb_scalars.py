"""Minimal dependency-free TensorBoard event-file scalar reader.

Why this exists: the lite-mono conda env has tensorboardX (writer) but no
tensorboard reader, so Snapshot 10's ema_distill/* diagnostics (notably the
canopy keep-ratio, the #1 design risk) were never directly inspected.
This script parses the TFRecord framing + Event protobuf by hand and dumps
matching scalar tags to CSV. Scalars written by tensorboardX use
Summary.Value.simple_value, which is all we need.

Usage:
  python read_tb_scalars.py <events_file> <tag_substring> <out_csv>
"""

import struct
import sys


def read_records(path):
    with open(path, "rb") as f:
        while True:
            header = f.read(8)
            if len(header) < 8:
                return
            (length,) = struct.unpack("<Q", header)
            f.read(4)  # length crc
            payload = f.read(length)
            if len(payload) < length:
                return
            f.read(4)  # payload crc
            yield payload


def parse_varint(buf, pos):
    result = 0
    shift = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not b & 0x80:
            return result, pos
        shift += 7


def parse_fields(buf):
    """Yield (field_number, wire_type, value) for one protobuf message."""
    pos = 0
    end = len(buf)
    while pos < end:
        key, pos = parse_varint(buf, pos)
        field, wire = key >> 3, key & 7
        if wire == 0:  # varint
            val, pos = parse_varint(buf, pos)
        elif wire == 1:  # 64-bit
            val = buf[pos:pos + 8]
            pos += 8
        elif wire == 2:  # length-delimited
            ln, pos = parse_varint(buf, pos)
            val = buf[pos:pos + ln]
            pos += ln
        elif wire == 5:  # 32-bit
            val = buf[pos:pos + 4]
            pos += 4
        else:
            return  # unsupported wire type; bail on this message
        yield field, wire, val


def extract_scalars(event_bytes):
    """Return (step, [(tag, value), ...]) from one Event proto."""
    step = 0
    scalars = []
    for field, wire, val in parse_fields(event_bytes):
        if field == 2 and wire == 0:  # Event.step
            step = val
        elif field == 5 and wire == 2:  # Event.summary
            for f2, w2, v2 in parse_fields(val):
                if f2 == 1 and w2 == 2:  # Summary.value (repeated)
                    tag, simple = None, None
                    for f3, w3, v3 in parse_fields(v2):
                        if f3 == 1 and w3 == 2:  # Value.tag
                            tag = v3.decode("utf-8", "replace")
                        elif f3 == 2 and w3 == 5:  # Value.simple_value
                            (simple,) = struct.unpack("<f", v3)
                    if tag is not None and simple is not None:
                        scalars.append((tag, simple))
    return step, scalars


def main():
    events_path, tag_filter, out_csv = sys.argv[1], sys.argv[2], sys.argv[3]
    tag_bytes = tag_filter.encode("utf-8")
    n_records = n_rows = 0
    with open(out_csv, "w", encoding="utf-8") as out:
        out.write("tag,step,value\n")
        for payload in read_records(events_path):
            n_records += 1
            if tag_bytes not in payload:
                continue
            step, scalars = extract_scalars(payload)
            for tag, value in scalars:
                if tag_filter in tag:
                    out.write("{},{},{}\n".format(tag, step, value))
                    n_rows += 1
    print("scanned {} records, wrote {} scalar rows to {}".format(
        n_records, n_rows, out_csv))


if __name__ == "__main__":
    main()
