from __future__ import annotations

from io import BytesIO
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import ZipFile

MAIN_NS = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = {"rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
PKG_REL_NS = {"pkg": "http://schemas.openxmlformats.org/package/2006/relationships"}


def parse_xlsx_bytes(file_bytes: bytes) -> str:
    with ZipFile(BytesIO(file_bytes)) as archive:
        workbook_path = _resolve_workbook_path(archive)
        workbook_root = ET.fromstring(archive.read(workbook_path))
        workbook_rels = _load_relationships(archive, workbook_path)
        shared_strings = _load_shared_strings(archive)

        sections: list[str] = []
        for sheet in workbook_root.findall("main:sheets/main:sheet", MAIN_NS):
            sheet_name = sheet.attrib.get("name", "Sheet")
            relationship_id = sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            if not relationship_id:
                continue
            target = workbook_rels.get(relationship_id)
            if not target:
                continue
            sheet_path = _normalize_zip_path(PurePosixPath(workbook_path).parent, target)
            rows = _extract_sheet_rows(archive.read(sheet_path), shared_strings)
            if rows:
                sections.append(f"[{sheet_name}]\n" + "\n".join(rows))

        return "\n\n".join(section for section in sections if section).strip()


def _resolve_workbook_path(archive: ZipFile) -> str:
    rels_root = ET.fromstring(archive.read("_rels/.rels"))
    for relation in rels_root.findall("pkg:Relationship", PKG_REL_NS):
        if relation.attrib.get("Type", "").endswith("/officeDocument"):
            return relation.attrib["Target"]
    return "xl/workbook.xml"


def _load_relationships(archive: ZipFile, base_path: str) -> dict[str, str]:
    base = PurePosixPath(base_path)
    rels_path = str(base.parent / "_rels" / f"{base.name}.rels")
    if rels_path not in archive.namelist():
        return {}
    rels_root = ET.fromstring(archive.read(rels_path))
    return {
        relation.attrib["Id"]: relation.attrib["Target"]
        for relation in rels_root.findall("pkg:Relationship", PKG_REL_NS)
        if relation.attrib.get("Id") and relation.attrib.get("Target")
    }


def _load_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for item in root.findall("main:si", MAIN_NS):
        fragments = [node.text or "" for node in item.findall(".//main:t", MAIN_NS)]
        values.append("".join(fragments).strip())
    return values


def _extract_sheet_rows(sheet_bytes: bytes, shared_strings: list[str]) -> list[str]:
    root = ET.fromstring(sheet_bytes)
    rows: list[str] = []
    for row in root.findall(".//main:sheetData/main:row", MAIN_NS):
        values: list[str] = []
        for cell in row.findall("main:c", MAIN_NS):
            value = _extract_cell_value(cell, shared_strings)
            if value:
                values.append(value)
        if values:
            rows.append(" | ".join(values))
    return rows


def _extract_cell_value(cell: ET.Element, shared_strings: list[str]) -> str:
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join(node.text or "" for node in cell.findall(".//main:t", MAIN_NS)).strip()

    value_node = cell.find("main:v", MAIN_NS)
    if value_node is None or value_node.text is None:
        return ""
    raw_value = value_node.text.strip()
    if not raw_value:
        return ""
    if cell_type == "s":
        index = int(raw_value)
        if 0 <= index < len(shared_strings):
            return shared_strings[index]
        return ""
    return raw_value


def _normalize_zip_path(base_dir: PurePosixPath, target: str) -> str:
    normalized = (base_dir / target).as_posix()
    parts: list[str] = []
    for part in normalized.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)
