#!/usr/bin/env python3
"""
Groq AI Test Generator + Auto-Fixer
-------------------------------------
1. Finds all Service and Controller Java files
2. Generates JUnit 5 + Mockito tests via Groq AI
3. Runs mvn test
4. If errors — sends errors back to Groq to fix the test files
5. Fixes pom.xml if missing dependencies
6. Repeats until all tests pass or max retries reached
"""

import os
import re
import glob
import json
import urllib.request
import urllib.error
import sys
import subprocess

MAX_FIX_RETRIES = 3
SRC_ROOT        = "src/main/java"
TEST_ROOT       = "src/test/java"
GROQ_API_URL    = "https://api.groq.com/openai/v1/chat/completions"
MODEL           = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────────
#  Load .env
# ─────────────────────────────────────────────

def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())
        print("✅ Loaded .env file")
    else:
        print("⚠️  No .env file found — using environment variables")

load_env()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


# ─────────────────────────────────────────────
#  Pretty printing
# ─────────────────────────────────────────────

def banner(msg):
    print(f"\n{'═'*60}")
    print(f"  {msg}")
    print(f"{'═'*60}")

def step(msg):
    print(f"\n── {msg}")

def success(msg):
    print(f"   ✅ {msg}")

def warn(msg):
    print(f"   ⚠️  {msg}")

def error(msg):
    print(f"   ❌ {msg}")


# ─────────────────────────────────────────────
#  Path normalisation helper
#  Always returns forward-slash relative path
#  starting from src/test/java or src/main/java
# ─────────────────────────────────────────────

def normalise_path(p: str) -> str:
    """
    Convert any absolute or mixed-separator path to a normalised
    relative path starting from 'src/', using os.sep.
    e.g.  D:\\work\\autotest\\src\\test\\java\\Foo.java
          → src/test/java/Foo.java  (forward slash, relative)
    """
    p = p.replace("\\", "/")
    for marker in ("src/test/java/", "src/main/java/"):
        if marker in p:
            return marker + p.split(marker, 1)[1]
    # fallback — just strip leading drive/abs prefix
    if p.startswith("/"):
        parts = p.lstrip("/").split("/")
        for i, part in enumerate(parts):
            if part == "src":
                return "/".join(parts[i:])
    return p


def norm(p: str) -> str:
    """normalise_path then convert to os.sep"""
    return normalise_path(p).replace("/", os.sep)


# ─────────────────────────────────────────────
#  Install groq SDK if missing
# ─────────────────────────────────────────────

def ensure_groq_sdk():
    try:
        import groq
        success("groq SDK already installed")
    except ImportError:
        print("📦 Installing groq SDK...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "groq", "-q"])
        success("groq SDK installed")


# ─────────────────────────────────────────────
#  Groq API call
# ─────────────────────────────────────────────

def call_groq(system_prompt, user_prompt):
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4096
        )
        return response.choices[0].message.content.strip()
    except ImportError:
        pass
    except Exception as e:
        warn(f"SDK error: {e} — trying HTTP fallback...")

    payload = json.dumps({
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4096
    }).encode("utf-8")

    req = urllib.request.Request(
        GROQ_API_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type":  "application/json",
            "User-Agent":    "groq-python/0.11.0",
            "Accept":        "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        error(f"HTTP {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        error(f"Request failed: {e}")
        return None


# ─────────────────────────────────────────────
#  Java file utilities
# ─────────────────────────────────────────────

def find_java_files():
    pattern = os.path.join(SRC_ROOT, "**", "*.java")
    all_files = glob.glob(pattern, recursive=True)
    targets = []
    for f in all_files:
        name = os.path.basename(f)
        if name.endswith("Service.java") or name.endswith("Controller.java"):
            if not name.endswith("Test.java"):
                targets.append(f)
    return targets

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def extract_package(content):
    m = re.search(r"^package\s+([\w.]+);", content, re.MULTILINE)
    return m.group(1) if m else ""

def extract_class_name(content):
    m = re.search(r"public\s+class\s+(\w+)", content)
    return m.group(1) if m else ""

def clean_code(content):
    content = re.sub(r"^```java\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"^```\s*$",    "", content, flags=re.MULTILINE)
    return content.strip()


# ─────────────────────────────────────────────
#  resolve_test_file
#  Given any path key from parse_errors, return
#  the actual path on disk (or None).
# ─────────────────────────────────────────────

def resolve_test_file(test_path: str):
    # 1. Direct hit
    if os.path.exists(test_path):
        return test_path

    # 2. Normalise and try again
    candidate = norm(test_path)
    if os.path.exists(candidate):
        return candidate

    # 3. Search by filename
    filename = os.path.basename(test_path)
    if not filename.endswith(".java"):
        filename += ".java"
    matches = glob.glob(os.path.join(TEST_ROOT, "**", filename), recursive=True)
    if matches:
        return matches[0]

    return None


# ─────────────────────────────────────────────
#  find_source_for_test
#  Given a resolved test path, find the best
#  matching entry in source_map / generated.
# ─────────────────────────────────────────────

def find_source_for_test(test_path: str, generated: dict, source_map: dict) -> str:
    test_norm = norm(test_path)

    # 1. Direct lookup (normalised keys)
    for gen_path, orig_path in generated.items():
        if norm(gen_path) == test_norm:
            return source_map.get(orig_path, "")

    # 2. Match by basename — e.g. CalculatorServiceTest.java → CalculatorService.java
    test_base = os.path.basename(test_norm)                  # CalculatorServiceTest.java
    src_base  = test_base.replace("Test.java", ".java")      # CalculatorService.java

    for gen_path, orig_path in generated.items():
        if os.path.basename(gen_path) == test_base:
            return source_map.get(orig_path, "")
        if os.path.basename(orig_path) == src_base:
            return source_map.get(orig_path, "")

    return ""


# ─────────────────────────────────────────────
#  Post-process: fix known Groq mistakes
# ─────────────────────────────────────────────

def post_process(code: str, is_controller: bool) -> str:

    # ── 1. Wrong @MockBean import ──────────────────────────────
    code = code.replace(
        "import org.mockito.MockBean;",
        "import org.springframework.boot.test.mock.mockito.MockBean;"
    )

    # ── 2. Missing static Mockito imports ──────────────────────
    needs_mockito_static = any(
        kw in code for kw in [
            "when(", "verify(", "doReturn(", "doThrow(",
            "any(", "eq(", "times(", "never(", "given("
        ]
    )
    has_mockito_static = "import static org.mockito.Mockito" in code
    if needs_mockito_static and not has_mockito_static:
        if "import org.mockito" in code:
            code = re.sub(
                r"(import org\.mockito[^;]+;)",
                r"\1\nimport static org.mockito.Mockito.*;",
                code, count=1
            )
        else:
            code = re.sub(
                r"(^package[^;]+;)",
                r"\1\n\nimport static org.mockito.Mockito.*;",
                code, flags=re.MULTILINE, count=1
            )

    # ── 3. @InjectMocks without @ExtendWith → NPE ──────────────
    has_inject   = "@InjectMocks"  in code
    has_extend   = "@ExtendWith"   in code
    has_webmvc   = "@WebMvcTest"   in code
    has_springbt = "@SpringBootTest" in code

    if has_inject and not has_extend and not has_webmvc and not has_springbt:
        if "import org.junit.jupiter.api.extension.ExtendWith;" not in code:
            code = re.sub(
                r"(^package[^;]+;)",
                (r"\1\n\nimport org.junit.jupiter.api.extension.ExtendWith;"
                 r"\nimport org.mockito.junit.jupiter.MockitoExtension;"),
                code, flags=re.MULTILINE, count=1
            )
        code = re.sub(
            r"(public\s+class\s+\w+)",
            r"@ExtendWith(MockitoExtension.class)\n\1",
            code, count=1
        )

    # ── 4. @ExtendWith present but imports missing ─────────────
    if "@ExtendWith(MockitoExtension.class)" in code:
        if "import org.mockito.junit.jupiter.MockitoExtension;" not in code:
            code = re.sub(
                r"(^package[^;]+;)",
                r"\1\nimport org.mockito.junit.jupiter.MockitoExtension;",
                code, flags=re.MULTILINE, count=1
            )
        if "import org.junit.jupiter.api.extension.ExtendWith;" not in code:
            code = re.sub(
                r"(^package[^;]+;)",
                r"\1\nimport org.junit.jupiter.api.extension.ExtendWith;",
                code, flags=re.MULTILINE, count=1
            )

    # ── 5. Controller: ensure MockMvc static imports present ───
    if is_controller and "@WebMvcTest" in code:
        mvc_statics = [
            ("MockMvcRequestBuilders",
             "import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;"),
            ("MockMvcResultMatchers",
             "import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;"),
        ]
        for marker, imp in mvc_statics:
            if marker not in code:
                code = re.sub(
                    r"(^package[^;]+;)",
                    rf"\1\n{imp}",
                    code, flags=re.MULTILINE, count=1
                )

    # ── 6. ALWAYS ensure core JUnit 5 imports are present ──────
    #       Groq frequently uses @Test / @DisplayName / @BeforeEach
    #       but forgets the imports — this is the root cause of
    #       "cannot find symbol: class Test" compile errors.
    junit5_imports = [
        ("@Test",         "import org.junit.jupiter.api.Test;"),
        ("@DisplayName",  "import org.junit.jupiter.api.DisplayName;"),
        ("@BeforeEach",   "import org.junit.jupiter.api.BeforeEach;"),
        ("@AfterEach",    "import org.junit.jupiter.api.AfterEach;"),
        ("@BeforeAll",    "import org.junit.jupiter.api.BeforeAll;"),
        ("@AfterAll",     "import org.junit.jupiter.api.AfterAll;"),
        ("@Disabled",     "import org.junit.jupiter.api.Disabled;"),
        ("@ParameterizedTest", "import org.junit.jupiter.params.ParameterizedTest;"),
        ("Assertions.",   "import org.junit.jupiter.api.Assertions;"),
        ("assertEquals",  "import static org.junit.jupiter.api.Assertions.*;"),
        ("assertNotNull", "import static org.junit.jupiter.api.Assertions.*;"),
        ("assertThrows",  "import static org.junit.jupiter.api.Assertions.*;"),
        ("assertTrue",    "import static org.junit.jupiter.api.Assertions.*;"),
        ("assertFalse",   "import static org.junit.jupiter.api.Assertions.*;"),
        ("assertNull",    "import static org.junit.jupiter.api.Assertions.*;"),
    ]

    # Deduplicate: only add each import once
    already_added = set()
    for annotation, imp in junit5_imports:
        if imp in already_added:
            continue
        if annotation in code and imp not in code:
            code = re.sub(
                r"(^package[^;]+;)",
                rf"\1\n{imp}",
                code, flags=re.MULTILINE, count=1
            )
            already_added.add(imp)

    return code


# ─────────────────────────────────────────────
#  STEP 1: Generate tests
# ─────────────────────────────────────────────

def generate_test(java_path):
    filename   = os.path.basename(java_path)
    content    = read_file(java_path)
    package    = extract_package(content)
    class_name = extract_class_name(content)
    is_ctrl    = "Controller" in filename

    if is_ctrl:
        mock_note = (
            "Use @WebMvcTest(ControllerClass.class) on the test class.\n"
            "Inject MockMvc with @Autowired private MockMvc mockMvc;\n"
            "Mock service dependencies with @MockBean "
            "(import org.springframework.boot.test.mock.mockito.MockBean — "
            "NOT org.mockito.MockBean which does not exist).\n"
            "Use mockMvc.perform(get/post/put/delete(...)) with andExpect() for assertions.\n"
            "Stub service calls with: when(service.method(any())).thenReturn(value);\n"
            "Required static imports:\n"
            "  import static org.mockito.Mockito.*;\n"
            "  import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;\n"
            "  import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;"
        )
    else:
        mock_note = (
            "REQUIRED: Annotate the test class with @ExtendWith(MockitoExtension.class).\n"
            "Without this annotation, @InjectMocks is NEVER initialised "
            "and every test throws NullPointerException.\n"
            "Use @Mock for each dependency field.\n"
            "Use @InjectMocks for the class under test.\n"
            "Required imports:\n"
            "  import org.junit.jupiter.api.extension.ExtendWith;\n"
            "  import org.mockito.junit.jupiter.MockitoExtension;\n"
            "  import org.mockito.Mock;\n"
            "  import org.mockito.InjectMocks;\n"
            "  import static org.mockito.Mockito.*;\n"
            "Do NOT use @MockBean or @SpringBootTest — pure unit test, no Spring context."
        )

    system = (
        "You are an expert Java developer specialising in JUnit 5 and Mockito.\n"
        "Output ONLY raw Java code — no markdown, no code fences, no explanation.\n\n"
        "HARD RULES (each violation causes compile or runtime failure):\n"
        "1.  @MockBean       → import org.springframework.boot.test.mock.mockito.MockBean;\n"
        "2.  @Mock           → import org.mockito.Mock;\n"
        "3.  @InjectMocks    → import org.mockito.InjectMocks;\n"
        "4.  when()/verify() → import static org.mockito.Mockito.*;\n"
        "5.  NEVER write 'import org.mockito.MockBean' — that class does not exist.\n"
        "6.  Service tests: class MUST have @ExtendWith(MockitoExtension.class).\n"
        "    Omitting it means @InjectMocks is null → NullPointerException.\n"
        "7.  Controller tests: @WebMvcTest(XController.class) on the class.\n"
        "8.  Every @Test method must contain at least one assertion.\n"
        "9.  ALWAYS import: import org.junit.jupiter.api.Test;\n"
        "10. ALWAYS import: import org.junit.jupiter.api.DisplayName;\n"
        "11. ALWAYS import: import org.junit.jupiter.api.BeforeEach; (if @BeforeEach used)\n"
        "12. ALWAYS import: import static org.junit.jupiter.api.Assertions.*;\n"
        "13. Every annotation used MUST have a corresponding import statement.\n"
        "14. Do NOT rely on star imports for JUnit 5 annotations — be explicit."
    )

    user = f"""Generate a complete JUnit 5 test class for this Java file.

Rules:
- JUnit 5 only (@Test, @BeforeEach, @DisplayName)
- {mock_note}
- Cover every public method: happy path + edge cases
- Meaningful camelCase test method names
- Package: {package}
- Class name: {class_name}Test
- Output ONLY raw Java starting from the package declaration

CRITICAL IMPORT REQUIREMENTS — include ALL of these that you use:
  import org.junit.jupiter.api.Test;
  import org.junit.jupiter.api.DisplayName;
  import org.junit.jupiter.api.BeforeEach;
  import static org.junit.jupiter.api.Assertions.*;

Source file ({filename}):
{content}"""

    result = call_groq(system, user)
    if not result:
        return None, None

    result = clean_code(result)
    result = post_process(result, is_ctrl)

    pkg   = extract_package(result)
    cname = extract_class_name(result)

    if not cname:
        warn(f"Could not extract class name from generated test for {filename}")
        return None, None

    if pkg:
        dest_dir = os.path.join(TEST_ROOT, pkg.replace(".", os.sep))
    else:
        rel      = java_path.replace(SRC_ROOT + os.sep, "").replace(SRC_ROOT + "/", "")
        dest_dir = os.path.join(TEST_ROOT, os.path.dirname(rel))

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"{cname}.java")
    write_file(dest_path, result)
    success(f"Generated: {dest_path}")
    return dest_path, result


# ─────────────────────────────────────────────
#  STEP 2: Run mvn test
# ─────────────────────────────────────────────

def run_maven_test():
    step("Running: mvn test")
    result = subprocess.run(
        "mvn test",
        shell=True,
        capture_output=True,
        text=True
    )
    output = result.stdout + result.stderr
    print(output[-5000:])
    return result.returncode == 0, output


# ─────────────────────────────────────────────
#  STEP 3: Parse errors from mvn output
# ─────────────────────────────────────────────

def parse_errors(mvn_output):
    errors = {}

    # ── A. Compilation errors — Linux absolute path ─────────────
    # [ERROR] /abs/path/src/test/java/Foo.java:[7,19] msg
    for m in re.finditer(
        r"\[ERROR\]\s+(/[^\s:\[]+\.java)\s*[\[:](\d+)[,\d\]]*\s*(.*)",
        mvn_output
    ):
        abs_path, line, msg = m.groups()
        rel = norm(abs_path)
        errors.setdefault(rel, []).append(f"Line {line}: {msg.strip()}")

    # ── B. Compilation errors — Windows absolute path ───────────
    # [ERROR] D:\path\src\test\java\Foo.java:[7,19] msg
    for m in re.finditer(
        r"\[ERROR\]\s+([A-Za-z]:[\\\/][^\s:\[]+\.java)\s*[\[:](\d+)[,\d\]]*\s*(.*)",
        mvn_output
    ):
        abs_path, line, msg = m.groups()
        rel = norm(abs_path)
        errors.setdefault(rel, []).append(f"Line {line}: {msg.strip()}")

    # ── C. Runtime failures — Surefire compact format ───────────
    # [ERROR]   ClassName.methodName:lineNum  reason text
    for m in re.finditer(
        r"\[ERROR\]\s{2,}([\w]+)\.([\w]+):(\d+)\s+(.*)",
        mvn_output
    ):
        class_name, method, line, reason = m.groups()
        matches = glob.glob(
            os.path.join(TEST_ROOT, "**", f"{class_name}.java"), recursive=True
        )
        key = norm(matches[0]) if matches else class_name
        errors.setdefault(key, []).append(
            f"{method} line {line}: {reason.strip()}"
        )

    # ── D. Runtime failures — Surefire verbose format ───────────
    # [ERROR] com.example.FooTest > testBar  AssertionError
    for m in re.finditer(
        r"\[ERROR\]\s+([\w.]+)\s*[>–\-]\s*([\w]+)\s+(.*)",
        mvn_output
    ):
        fqcn, method, reason = m.groups()
        short   = fqcn.split(".")[-1]
        matches = glob.glob(
            os.path.join(TEST_ROOT, "**", f"{short}.java"), recursive=True
        )
        key = norm(matches[0]) if matches else short
        errors.setdefault(key, []).append(f"{method}: {reason.strip()}")

    # ── E. Fallback ─────────────────────────────────────────────
    if "BUILD FAILURE" in mvn_output and not errors:
        lines = [l for l in mvn_output.splitlines() if "[ERROR]" in l]
        errors["__general__"] = lines[:20]

    # ── Debug ────────────────────────────────────────────────────
    if errors:
        print(f"   🔍 Parsed errors in {len(errors)} file(s):")
        for path, msgs in errors.items():
            print(f"      • {path}: {len(msgs)} error(s)")
            for msg in msgs[:3]:
                print(f"        - {msg[:120]}")
    else:
        warn("No file-specific errors parsed from Maven output")

    return errors


# ─────────────────────────────────────────────
#  STEP 4: Fix a test file via Groq
# ─────────────────────────────────────────────

def fix_test_file(test_path, error_msgs, original_source):
    if test_path == "__general__":
        warn("General build error — trying pom.xml fix only")
        return False

    resolved = resolve_test_file(test_path)
    if not resolved:
        warn(f"Cannot find on disk: {test_path}")
        return False

    current_test = read_file(resolved)
    errors_text  = "\n".join(error_msgs)
    is_ctrl      = "Controller" in os.path.basename(resolved)

    step(f"Fixing: {os.path.basename(resolved)}")
    print("   Errors:")
    for e in error_msgs[:5]:
        print(f"     - {e[:120]}")

    system = (
        "You are an expert Java developer. Fix the broken JUnit 5 test file.\n"
        "Output ONLY the corrected raw Java code — no markdown, no explanation.\n\n"
        "HARD RULES:\n"
        "1.  @MockBean       → import org.springframework.boot.test.mock.mockito.MockBean;\n"
        "2.  @Mock           → import org.mockito.Mock;\n"
        "3.  @InjectMocks    → import org.mockito.InjectMocks;\n"
        "4.  when()/verify() → import static org.mockito.Mockito.*;\n"
        "5.  NEVER 'import org.mockito.MockBean' — does not exist.\n"
        "6.  Service tests MUST have @ExtendWith(MockitoExtension.class) on the class.\n"
        "    Without it, @InjectMocks is null → NullPointerException on every test.\n"
        "7.  Controller tests: @WebMvcTest(XController.class), no @ExtendWith needed.\n"
        "8.  Every @Test method must have at least one assertion.\n"
        "9.  ALWAYS include: import org.junit.jupiter.api.Test;\n"
        "10. ALWAYS include: import org.junit.jupiter.api.DisplayName;\n"
        "11. ALWAYS include: import org.junit.jupiter.api.BeforeEach; (if used)\n"
        "12. ALWAYS include: import static org.junit.jupiter.api.Assertions.*;\n"
        "13. Every annotation used MUST have a corresponding import — no exceptions."
    )

    user = f"""Fix this broken JUnit 5 test file.

ERRORS TO FIX:
{errors_text}

CURRENT BROKEN TEST FILE:
{current_test}

ORIGINAL SOURCE FILE (for context):
{original_source}

Instructions:
- Keep the exact same package and class name
- Fix ALL listed errors
- Do not remove any existing tests
- Ensure EVERY annotation has an explicit import (especially @Test and @DisplayName)
- Output ONLY the corrected raw Java starting from the package declaration"""

    fixed = call_groq(system, user)
    if not fixed:
        error("Groq returned no fix")
        return False

    fixed = clean_code(fixed)
    fixed = post_process(fixed, is_ctrl)

    if not extract_class_name(fixed):
        error("Fixed code has no class name — skipping")
        return False

    write_file(resolved, fixed)
    success(f"Fixed and saved: {resolved}")
    return True


# ─────────────────────────────────────────────
#  STEP 5: Fix pom.xml dependencies
# ─────────────────────────────────────────────

REQUIRED_DEPS = {
    "mockito-core": """        <dependency>
            <groupId>org.mockito</groupId>
            <artifactId>mockito-core</artifactId>
            <scope>test</scope>
        </dependency>""",

    "spring-boot-starter-test": """        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>""",

    "junit-jupiter": """        <dependency>
            <groupId>org.junit.jupiter</groupId>
            <artifactId>junit-jupiter</artifactId>
            <scope>test</scope>
        </dependency>""",
}

def fix_pom_if_needed(mvn_output):
    if not os.path.exists("pom.xml"):
        warn("pom.xml not found")
        return

    pom     = read_file("pom.xml")
    changed = False

    for artifact, dep_xml in REQUIRED_DEPS.items():
        if artifact not in pom:
            pom = pom.replace("</dependencies>", f"{dep_xml}\n    </dependencies>", 1)
            changed = True
            success(f"Added to pom.xml: {artifact}")

    if changed:
        write_file("pom.xml.bak", read_file("pom.xml"))
        write_file("pom.xml", pom)
        success("pom.xml updated (backup: pom.xml.bak)")
    else:
        success("pom.xml already has all required dependencies")


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    banner("🤖 Groq AI — Generate → Run → Fix → Repeat")

    if not GROQ_API_KEY:
        error("GROQ_API_KEY not set!")
        sys.exit(1)
    if not GROQ_API_KEY.startswith("gsk_"):
        warn(f"Key prefix looks unexpected: {GROQ_API_KEY[:10]}...")
    print(f"   🔑 Key: {GROQ_API_KEY[:8]}...{GROQ_API_KEY[-4:]}")

    ensure_groq_sdk()

    # ── Find source files ────────────────────────────
    step("Finding Service and Controller files...")
    java_files = find_java_files()

    if not java_files:
        warn("No Service or Controller files found in src/main/java")
        sys.exit(0)

    print(f"   Found {len(java_files)} file(s):")
    for f in java_files:
        print(f"   • {f}")

    # source_map keyed by NORMALISED path for reliable lookup
    source_map = { norm(f): read_file(f) for f in java_files }

    # ── STEP 1: Generate tests ───────────────────────
    banner("STEP 1 — Generating Tests")
    generated = {}   # normalised test path → normalised source path

    for java_path in java_files:
        step(f"Generating: {os.path.basename(java_path)}")
        test_path, _ = generate_test(java_path)
        if test_path:
            generated[norm(test_path)] = norm(java_path)

    if not generated:
        error("No tests were generated. Check your Groq API key.")
        sys.exit(1)

    print(f"\n   Generated {len(generated)} test file(s):")
    for t in generated:
        print(f"   • {t}")

    # ── STEP 2: Check pom.xml ────────────────────────
    banner("STEP 2 — Checking pom.xml")
    fix_pom_if_needed("")

    # ── STEP 3: Run → Fix loop ───────────────────────
    banner("STEP 3 — Run → Fix → Repeat")

    for attempt in range(1, MAX_FIX_RETRIES + 2):
        label = "First run" if attempt == 1 else f"Re-run after fix #{attempt - 1}"
        print(f"\n🧪 {label} (attempt {attempt} of {MAX_FIX_RETRIES + 1})...")

        passed, mvn_output = run_maven_test()

        if passed:
            banner("✅ ALL TESTS PASSED!")
            break

        if attempt > MAX_FIX_RETRIES:
            banner("❌ Max retries reached — manual review needed")
            sys.exit(1)

        print(f"\n🔧 Auto-fixing errors (round {attempt}/{MAX_FIX_RETRIES})...")
        errors_map = parse_errors(mvn_output)

        if not errors_map:
            warn("Could not parse specific errors — trying pom.xml fix only")
            fix_pom_if_needed(mvn_output)
            continue

        dep_keywords = ["cannot find symbol", "package does not exist", "classnotfoundexception"]
        if any(kw in mvn_output.lower() for kw in dep_keywords):
            fix_pom_if_needed(mvn_output)

        any_fixed = False
        for test_path_key, err_msgs in errors_map.items():
            if test_path_key == "__general__":
                fix_pom_if_needed(mvn_output)
                continue

            # ── Resolve source content for this test ──
            src_content = find_source_for_test(test_path_key, generated, source_map)
            if not src_content:
                warn(f"No matching source found for {test_path_key} — fixing without source context")

            if fix_test_file(test_path_key, err_msgs, src_content):
                any_fixed = True

        if not any_fixed:
            warn("Nothing was fixed this round — stopping loop")
            break

    # ── Final summary ─────────────────────────────────
    banner("Summary")
    print(f"  Source files : {len(java_files)}")
    print(f"  Tests created: {len(generated)}")
    print(f"\n  📂 Test files:")
    all_tests = glob.glob(os.path.join(TEST_ROOT, "**", "*.java"), recursive=True)
    for t in sorted(all_tests):
        print(f"     • {t}")


if __name__ == "__main__":
    main()