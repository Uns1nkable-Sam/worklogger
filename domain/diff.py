import difflib
import re
from copy import deepcopy
from typing import List, Dict, Tuple


class DiffChunk:
    def __init__(self, header: str):
        header_data = self._parse_header(header)
        try:
            self.ost = int(header_data[0])
            self.oln = int(header_data[1] if header_data[1] != '' else int(header_data[0]))
            self.nst = int(header_data[2])
            self.nln = int(header_data[3] if header_data[3] != '' else int(header_data[2]))
        except Exception as e:
            print(header, header_data)
            raise ValueError

        self.original_start = self.ost - 1 if self.ost > 0 else 0
        self.original_length = self.oln

        self.new_start = self.nst - 1 if self.nst > 0 else 0
        self.new_length = self.nln

        self.original_last_line = self.original_start + self.oln if self.oln > 0 else 0
        self.new_last_line = self.new_start + self.nln if self.nln > 0 else 0

        self.lines = []

    def to_string(self) -> str:
        return ''.join(self.lines)

    def to_full_string(self) -> str:
        header = f"@@ -{self.ost},{self.oln} +{self.nst},{self.nln} @@\n"
        return header + ''.join(self.lines)

    def _parse_header(self, header: str):
        m = re.match(r"^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@$", header)
        if not m:
            raise ValueError("Invalid patch string: " + header)
        return m.group(1), m.group(2), m.group(3), m.group(4)

    def apply(self, original_lines: List[str]):
        result = []

        original_len = len(original_lines)

        if original_len != self.original_length:
            print('Bad lines amount')

        i = 0
        for line in self.lines:
            op = line[0]
            text = line[1:]

            if op == " ":
                if text.strip(' \r\n\t') == original_lines[i].strip(' \r\n\t'):
                    result.append(original_lines[i])
                    i = i + 1
                else:
                    print("lines do not match for copy")

            elif op == "-":
                if text == original_lines[i]:
                    i = i + 1
                else:
                    print("lines do not match for removal")

            elif op == "+":
                result.append(text)

        if len(result) != self.new_length:
            print('Bad result lines amount')

        return result

    def revert(self, new_lines: List[str]):
        result = []
        if len(new_lines) != self.new_length:
            print('Bad lines amount')

        i = 0
        for line in self.lines:
            op = line[0]
            text = line[1:]

            if op == " ":
                if text.strip(' \r\n\t') == new_lines[i].strip(' \r\n\t'):
                    result.append(new_lines[i])
                    i = i + 1
                else:
                    print("lines do not match for copy")

            elif op == "-":
                # if text == new_lines[i]:
                result.append(text)
                # else:
                #     print("lines do not match for removal")

            elif op == "+" or op == "?":
                i = i + 1

            else:
                result.append(text)
                i = i + 1

        if len(result) != self.original_length:
            print('Bad result lines amount')

        return result


class FilePatch:
    def __init__(self):
        self.lines: List[str] = []
        self.original_file: str = None
        self.new_file: str = None
        self.is_deleted: bool = False
        self.is_new: bool = False
        self.chunks: List[DiffChunk] = []

    def file_name(self) -> str:
        if self.is_new:
            return self.new_file
        if self.is_deleted:
            return self.original_file
        return self.new_file

    def to_string(self) -> str:
        chunks = [chunk.to_string() for chunk in self.chunks]
        return ''.join(chunks)

    def to_full_string(self) -> str:
        a_name = self.original_file if self.original_file is not None else "dev/null"
        b_name = self.new_file if self.new_file is not None else "dev/null"

        a_name = a_name.removeprefix('/')
        b_name = b_name.removeprefix('/')

        header = f"diff --git a/{a_name} b/{b_name}\n--- a/{a_name}\n+++ b/{b_name}\n"
        chunks = [chunk.to_full_string() for chunk in self.chunks]
        return header + ''.join(chunks)

    def filename(self):
        if self.is_new:
            return self.new_file
        if self.is_deleted:
            return self.original_file
        return self.new_file

    def scan_chunks(self):
        current_chunk = None
        for line in self.lines:
            if line.startswith("@@"):
                current_chunk = DiffChunk(line)
                self.chunks.append(current_chunk)
            else:
                current_chunk.lines.append(line)

    def process(self):
        if self.new_file.startswith('+++'):
            self.new_file = self.new_file[4:].strip('\n')
            if self.new_file.startswith('b/'):
                self.new_file = self.new_file[2:]
        if self.original_file.startswith('---'):
            self.original_file = self.original_file[4:].strip('\n')
            if self.original_file.startswith('a/'):
                self.original_file = self.original_file[2:]
        if self.original_file == '/dev/null':
            self.is_new = True
        if self.new_file == '/dev/null':
            self.is_deleted = True
        self.scan_chunks()

    def apply(self, text: List[str]) -> List[str]:
        if len(self.chunks) == 0:
            return deepcopy(text)
        result = []

        prev_chunk_end = 0
        for chunk in self.chunks:
            if prev_chunk_end < chunk.original_start:
                result.extend(text[prev_chunk_end:chunk.original_start])

            lines_to_apply = deepcopy(text[chunk.original_start:chunk.original_last_line]) \
                if chunk.original_length > 0 else []
            applied_lines = chunk.apply(lines_to_apply)

            result.extend(applied_lines)
            prev_chunk_end = chunk.original_start + chunk.original_length
        if len(text) > prev_chunk_end:
            result.extend(text[prev_chunk_end:])

        return result

    def revert(self, text: List[str]) -> List[str]:
        if len(self.chunks) == 0:
            return deepcopy(text)
        result = []

        prev_chunk_end = 0
        for chunk in self.chunks:
            result.extend(text[prev_chunk_end:chunk.new_start])
            applied_lines = chunk.revert(deepcopy(text[chunk.new_start:chunk.new_last_line]))
            result.extend(applied_lines)
            prev_chunk_end = chunk.new_last_line

        if len(text) > prev_chunk_end:
            result.extend(text[prev_chunk_end:])

        return result


class Patch:
    def __init__(self, patch: List[str] | str, is_empty=False):
        if is_empty:
            self.diffs = {}
            self._patch_text = ''
            return
        if isinstance(patch, str):
            self._patch_text = patch.splitlines(keepends=True)
        else:
            self._patch_text = deepcopy(patch)

        self.diffs: Dict[str, FilePatch] = self._parse_diffs(self._patch_text)

    def get_files_with_extensions_only(self, extensions: List[str]) -> 'Patch':
        result = Patch([], True)
        for key, file_diff in self.diffs.items():
            filename = file_diff.filename()
            should_add = False
            for ext in extensions:
                if filename.endswith(ext):
                    should_add = True
                    break
            if should_add:
                result.diffs[key] = deepcopy(file_diff)

        result_patch = [file_diff.to_full_string() for key, file_diff in result.get_diffs().items()]
        result._patch_text = ''.join(result_patch)

        return result

    def to_string(self) -> str:
        return ''.join(self._patch_text)

    def get_diffs(self) -> Dict[str, FilePatch]:
        return self.diffs

    def _parse_diffs(self, patch: List[str]) -> Dict[str, FilePatch]:
        files = []
        current_file = None

        for line in patch:
            first_symbol = line[0]
            if first_symbol in ["-", "+", "@", " ", "?"]:
                if line.startswith("---"):
                    if current_file is None:
                        current_file = FilePatch()
                        files.append(current_file)
                    current_file.original_file = line
                elif line.startswith("+++"):
                    if current_file is None:
                        current_file = FilePatch()
                        files.append(current_file)
                    current_file.new_file = line
                else:
                    if line.startswith("@@"):
                        end = line.find('@@', 2)
                        if len(line.strip('\n')) <= end + 2:
                            current_file.lines.append(line.strip('\n'))
                        else:
                            current_file.lines.append(line[:end + 2])
                    else:
                        current_file.lines.append(line)
            else:
                if line.startswith('diff'):
                    current_file = FilePatch()
                    files.append(current_file)

        result = {}
        for f in files:
            if len(f.lines) > 0:
                f.process()
                result[f.file_name()] = f

        return result

    def get_changes_amounts(self) -> Tuple[int, int]:
        adds = 0
        removals = 0
        for line in self._patch_text:
            if line.startswith('+') and not line.startswith('+++'):
                adds += 1
            if line.startswith('-') and not line.startswith('---'):
                removals += 1
        return adds, removals

    def get_changes(self) -> Tuple[List[str], List[str]]:
        adds = []
        removals = []
        for line in self._patch_text:
            if line.startswith('+') and not line.startswith('+++'):
                adds.append(line.removeprefix('+').strip("\r\n\t "))
            if line.startswith('-') and not line.startswith('---'):
                removals.append(line.removeprefix('-').strip("\r\n\t "))
        return adds, removals

    def get_metrics(self) -> dict:
        adds, rems = self.get_changes_amounts()
        return {"lines": {"added": adds, "removed": rems}}


def compare_texts(self, text1, text2, name1, name2) -> Patch:
    diff = difflib.unified_diff(
        text1.splitlines(keepends=True),
        text2.splitlines(keepends=True),
        fromfile=name1,
        tofile=name2,
        lineterm=''
    )
    return Patch(list(diff))
