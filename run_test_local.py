#!/usr/bin/env python3
"""
Local EvoSuite Test Runner
--------------------------
Mirrors exactly what GitHub Actions does, but runs on your machine.
Run this before pushing to catch issues early.

Requirements:
  - Java 17+
  - Maven in PATH
  - Internet access (first run only, to download jars)

Usage:
  python run_tests_local.py
"""

import os
import re
import glob
import shutil
import subprocess
import urllib.request
import sys

# ─────────────────────────────────────────────
#  Config
# ─────────────────────────────────────────────
EVOSUITE_VERSION = "1.2.0"
EVOSUITE_JAR     = f"evosuite/evosuite-{EVOSUITE_VERSION}.jar"
EVOSUITE_URL     = (
    f"https://github.com/EvoSuite/evosuite/releases/download/"
    f"v{EVOSUITE_VERSION}/evosuite-{EVOSUITE_VERSION}.jar"
)

# Runtime jar — downloaded directly from GitHub releases
# This completely bypasses the broken evosuite.org/m2 Maven repository
EVOSUITE_RUNTIME_JAR = f"evosuite/evosuite-standalone-runtime-{EVOSUITE_VERSION}.jar"
EVOSUITE_RUNTIME_URL = (
    f"https://github.com/EvoSuite/evosuite/releases/download/"
    f"v{EVOSUITE_VERSION}/evosuite-standalone-runtime-{EVOSUITE_VERSION}.jar"
)

SEARCH_BUDGET = 60   # seconds per class — increase for better coverage
SRC_ROOT      = "src/main/java"
TEST_ROOT     = "src/test/java"
EVOSUITE_OUT  = "evosuite-tests"
POM_FILE      = "pom.xml"

EVOSUITE_RUNTIME_DEP = """        <dependency>
            <groupId>org.evosuite</groupId>
            <artifactId>evosuite-standalone-runtime</artifactId>
            <version>1.2.0</version>
            <scope>test</scope>
        </dependency>"""


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def run(cmd: str, capture: bool = False) -> tuple[int, str]:
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if capture:
        return result.returncode, result.stdout + result.stderr
    return result.returncode, ""


def banner(msg: str) -> None:
    print(f"\n{'═'*60}")
    print(f"  {msg}")
    print(f"{'═'*60}")


def step(msg: str) -> None:
    print(f"\n── {msg}")


def download_file(url: str, dest: str, label: str) -> bool:
    print(f"   Fetching {label}…")
    try:
        urllib.request.urlretrieve(url, dest)
        size_kb = os.path.getsize(dest) // 1024
        print(f"   ✅ Saved to {dest} ({size_kb} KB)")
        return True
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return False


# ─────────────────────────────────────────────
#  Step 0: Fix misplaced test files in src/main
# ─────────────────────────────────────────────

def fix_misplaced_test_files():
    """Move any *Test.java files from src/main/java to src/test/java."""
    step("Scanning for misplaced test files in src/main/java…")
    pattern = os.path.join(SRC_ROOT, "**", "*Test.java")
    misplaced = glob.glob(pattern, recursive=True)

    if not misplaced:
        print("   ✅ No misplaced test files found.")
        return

    print(f"   ⚠️  Found {len(misplaced)} misplaced test file(s) — moving to src/test/java:")
    for src_path in misplaced:
        dest_path = src_path.replace(
            os.path.join("src", "main", "java"),
            os.path.join("src", "test", "java"), 1
        )
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.move(src_path, dest_path)
        print(f"   🚚 {src_path}  →  {dest_path}")
    print("   ✅ All misplaced files moved.")


# ─────────────────────────────────────────────
#  Step 1: Download EvoSuite jars
# ─────────────────────────────────────────────

def ensure_evosuite():
    os.makedirs("evosuite", exist_ok=True)

    if os.path.exists(EVOSUITE_JAR):
        print(f"✅ EvoSuite jar found: {EVOSUITE_JAR}")
    else:
        step("Downloading EvoSuite jar…")
        if not download_file(EVOSUITE_URL, EVOSUITE_JAR, "evosuite.jar"):
            sys.exit(1)

    if os.path.exists(EVOSUITE_RUNTIME_JAR):
        print(f"✅ EvoSuite runtime jar found: {EVOSUITE_RUNTIME_JAR}")
    else:
        step("Downloading EvoSuite standalone runtime jar…")
        if not download_file(EVOSUITE_RUNTIME_URL, EVOSUITE_RUNTIME_JAR,
                             "evosuite-standalone-runtime.jar"):
            sys.exit(1)


# ─────────────────────────────────────────────
#  Step 2: Install runtime jar into local .m2
# ─────────────────────────────────────────────

def install_runtime_to_local_repo():
    """
    Install the runtime jar directly into ~/.m2 using mvn install:install-file.
    This completely bypasses the broken evosuite.org/m2 Maven repository.
    Maven will find it locally — no internet needed after this step.
    """
    step("Installing EvoSuite runtime into local Maven repository (~/.m2)…")

    m2_jar = os.path.join(
        os.path.expanduser("~"), ".m2", "repository",
        "org", "evosuite", "evosuite-standalone-runtime",
        EVOSUITE_VERSION,
        f"evosuite-standalone-runtime-{EVOSUITE_VERSION}.jar"
    )

    # Already installed and valid (not a placeholder/empty file)
    if os.path.exists(m2_jar) and os.path.getsize(m2_jar) > 10_000:
        print(f"   ✅ Already in local repo ({os.path.getsize(m2_jar)//1024} KB) — skipping install")
        return

    # Remove stale broken cache so mvn install:install-file can write cleanly
    m2_dir = os.path.dirname(m2_jar)
    if os.path.exists(m2_dir):
        shutil.rmtree(m2_dir)
        print("   🗑️  Removed stale .m2 cache directory")

    abs_jar = os.path.abspath(EVOSUITE_RUNTIME_JAR)
    cmd = (
        f'mvn install:install-file '
        f'-Dfile="{abs_jar}" '
        f'-DgroupId=org.evosuite '
        f'-DartifactId=evosuite-standalone-runtime '
        f'-Dversion={EVOSUITE_VERSION} '
        f'-Dpackaging=jar '
        f'-DgeneratePom=true '
        f'-q'
    )
    code, out = run(cmd, capture=True)
    if code == 0:
        size_kb = os.path.getsize(m2_jar) // 1024 if os.path.exists(m2_jar) else 0
        print(f"   ✅ Installed into local repo ({size_kb} KB)")
        print(f"   📍 {m2_jar}")
    else:
        print(f"   ❌ Install failed:\n{out}")
        sys.exit(1)


# ─────────────────────────────────────────────
#  Step 3: Patch pom.xml
# ─────────────────────────────────────────────

def patch_pom():
    step("Checking pom.xml for EvoSuite runtime dependency…")
    if not os.path.exists(POM_FILE):
        print(f"   ⚠️  {POM_FILE} not found — skipping.")
        return

    with open(POM_FILE, "r", encoding="utf-8") as f:
        pom = f.read()

    changed = False

    # Remove broken evosuite.org repo entry if it snuck in from a previous run
    if "evosuite.org" in pom:
        print("   🧹 Removing broken evosuite.org repository entry…")
        pom = re.sub(
            r'\s*<repository>\s*<id>EvoSuite</id>.*?</repository>',
            '', pom, flags=re.DOTALL
        )
        pom = re.sub(r'\s*<repositories>\s*</repositories>', '', pom)
        changed = True
        print("   ✅ Removed — runtime is now served from local ~/.m2")

    # Add dependency if missing
    if "evosuite-standalone-runtime" not in pom:
        if not changed:
            with open(POM_FILE + ".bak", "w", encoding="utf-8") as f:
                f.write(pom)
            print("   📦 Backup saved to pom.xml.bak")
        pom = pom.replace(
            "</dependencies>",
            f"{EVOSUITE_RUNTIME_DEP}\n    </dependencies>",
            1
        )
        changed = True
        print("   ✅ Added evosuite-standalone-runtime to pom.xml")
        print("   ℹ️  Resolved from local ~/.m2 — no external repository needed")
    else:
        print("   ✅ EvoSuite runtime dependency already in pom.xml")

    if changed:
        with open(POM_FILE, "w", encoding="utf-8") as f:
            f.write(pom)


# ─────────────────────────────────────────────
#  Step 4: Compile
# ─────────────────────────────────────────────

def compile_project() -> bool:
    step("Compiling project (mvn compile)…")
    code, _ = run("mvn compile -q")
    if code != 0:
        print("❌ Compilation failed. Fix source errors before generating tests.")
        return False
    print("✅ Compilation successful.")
    return True


# ─────────────────────────────────────────────
#  Step 5: Build classpath
# ─────────────────────────────────────────────

def get_classpath() -> str:
    step("Resolving Maven classpath…")
    cp_file = "target/cp.txt"
    run(f"mvn -q dependency:build-classpath -Dmdep.outputFile={cp_file}", capture=True)
    cp_line = ""
    if os.path.exists(cp_file):
        with open(cp_file, "r") as f:
            cp_line = f.read().strip()
        os.remove(cp_file)
    full_cp = f"target/classes{os.pathsep}{cp_line}"
    print(f"   ✅ Classpath resolved ({len(full_cp)} chars)")
    return full_cp


# ─────────────────────────────────────────────
#  Step 6: Find Service & Controller classes
# ─────────────────────────────────────────────

def find_target_classes() -> list[str]:
    pattern = os.path.join("target", "classes", "**", "*.class")
    results = []
    for path in glob.glob(pattern, recursive=True):
        basename = os.path.basename(path)
        if "$" in basename:
            continue
        if not (basename.endswith("Service.class") or basename.endswith("Controller.class")):
            continue
        fqcn = (path
                .replace("target" + os.sep + "classes" + os.sep, "")
                .replace(os.sep, ".")
                .replace(".class", ""))
        results.append(fqcn)
    return results


# ─────────────────────────────────────────────
#  Step 7: Generate tests with EvoSuite
# ─────────────────────────────────────────────

def generate_tests(classes: list[str], classpath: str) -> bool:
    step(f"Generating tests for {len(classes)} class(es)…")
    os.makedirs(EVOSUITE_OUT, exist_ok=True)
    any_generated = False

    for fqcn in classes:
        print(f"\n   ⚙️  {fqcn}")
        cmd = (
            f'java -jar {EVOSUITE_JAR} '
            f'-class {fqcn} '
            f'-projectCP "{classpath}" '
            f'-Dsearch_budget={SEARCH_BUDGET} '
            f'-Dassertion_strategy=mutation '
            f'-Dcriterion=BRANCH:LINE:EXCEPTION '
            f'-base_dir {EVOSUITE_OUT}'
        )
        code, out = run(cmd, capture=True)
        if code == 0:
            print("      ✅ Generated")
            any_generated = True
        else:
            print("      ⏭️  Skipped (abstract/interface/no public methods)")
            lines = [l for l in out.splitlines() if l.strip()]
            for l in lines[-3:]:
                print(f"         {l}")

    return any_generated


# ─────────────────────────────────────────────
#  Step 8: Copy tests to src/test/java
# ─────────────────────────────────────────────

def copy_tests_to_src():
    step("Copying generated tests to src/test/java…")
    pattern = os.path.join(EVOSUITE_OUT, "**", "*_ESTest.java")
    test_files = glob.glob(pattern, recursive=True)

    if not test_files:
        print("   ⚠️  No *_ESTest.java files found in evosuite-tests/")
        all_files = glob.glob(os.path.join(EVOSUITE_OUT, "**", "*"), recursive=True)
        if all_files:
            print("   📁 Contents of evosuite-tests/:")
            for f in all_files[:15]:
                print(f"      {f}")
        return

    for f in test_files:
        basename = os.path.basename(f)
        original_class = basename.replace("_ESTest.java", "")
        subdir = "controller" if "Controller" in original_class else "service"

        with open(f, "r", encoding="utf-8") as fp:
            content = fp.read()

        pkg_match = re.search(r"^package\s+([\w.]+);", content, re.MULTILINE)
        if pkg_match:
            pkg_path = pkg_match.group(1).replace(".", os.sep)
            dest_dir = os.path.join(TEST_ROOT, pkg_path)
        else:
            java_files = glob.glob(os.path.join(SRC_ROOT, "**", "*.java"), recursive=True)
            base_pkg = ""
            if java_files:
                sample = java_files[0].replace("\\", "/")
                m = re.search(r"src/main/java/(.+)/[^/]+\.java", sample)
                if m:
                    parts = m.group(1).split("/")
                    clean = [p for p in parts
                             if p.lower() not in ("service","services","controller","controllers")]
                    base_pkg = os.path.join(*clean) if clean else ""
            dest_dir = os.path.join(TEST_ROOT, base_pkg, subdir)

        os.makedirs(dest_dir, exist_ok=True)
        with open(os.path.join(dest_dir, basename), "w", encoding="utf-8") as fp:
            fp.write(content)
        print(f"   ✅ {basename}  →  {dest_dir}")

        scaffold = f.replace("_ESTest.java", "_ESTest_scaffolding.java")
        if os.path.exists(scaffold):
            with open(scaffold, "r") as fp:
                sc = fp.read()
            with open(os.path.join(dest_dir, os.path.basename(scaffold)), "w") as fp:
                fp.write(sc)


# ─────────────────────────────────────────────
#  Step 9: Run tests
# ─────────────────────────────────────────────

def run_tests() -> bool:
    step("Running all tests (mvn test)…")
    code, _ = run("mvn test")
    if code == 0:
        print("\n✅ ALL TESTS PASSED")
        return True
    else:
        print("\n❌ SOME TESTS FAILED — check output above")
        return False


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def main():
    banner("🚀 EvoSuite Auto Test Generator")

    if not os.path.exists("pom.xml"):
        print("❌ pom.xml not found. Run this from your project root.")
        sys.exit(1)

    fix_misplaced_test_files()   # Step 0: move any *Test.java out of src/main
    ensure_evosuite()             # Step 1: download both jars from GitHub
    install_runtime_to_local_repo()  # Step 2: install runtime into ~/.m2
    patch_pom()                   # Step 3: add dep to pom.xml, clean broken repo

    if not compile_project():     # Step 4
        sys.exit(1)

    classpath = get_classpath()   # Step 5
    classes   = find_target_classes()  # Step 6

    if not classes:
        print("\n⚠️  No Service/Controller classes found in target/classes.")
        sys.exit(1)

    banner(f"Found {len(classes)} class(es) to test")
    for c in classes:
        print(f"   • {c}")

    generated = generate_tests(classes, classpath)  # Step 7
    if not generated:
        print("\n⚠️  No tests were generated.")
        sys.exit(1)

    copy_tests_to_src()           # Step 8

    banner("Test Results")
    success = run_tests()         # Step 9

    banner("Summary")
    print(f"  Classes processed : {len(classes)}")
    test_files = glob.glob(os.path.join(TEST_ROOT, "**", "*_ESTest.java"), recursive=True)
    print(f"  Test files created: {len(test_files)}")
    for t in test_files:
        print(f"    • {t}")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()