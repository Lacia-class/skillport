import asyncio
import os
import tempfile

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from skillport.modules.skills.internal.manager import BUILTIN_SKILLS


def setup_test_skills(skills_dir: str) -> None:
    """Set up test skills directory with hello-world skill."""
    os.makedirs(skills_dir, exist_ok=True)

    # Create hello-world skill from built-in content
    hello_world_dir = os.path.join(skills_dir, "hello-world")
    os.makedirs(hello_world_dir, exist_ok=True)

    skill_content = BUILTIN_SKILLS.get("hello-world", "")
    with open(os.path.join(hello_world_dir, "SKILL.md"), "w") as f:
        f.write(skill_content)


async def run_test():
    # Use temp dirs for everything to be self-contained
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = os.path.join(tmpdir, "skills")
        db_path = os.path.join(tmpdir, "skills.lancedb")

        # Set up test skills
        setup_test_skills(skills_dir)

        # Configure environment for the server
        server_env = os.environ.copy()
        server_env["SKILLPORT_SKILLS_DIR"] = skills_dir
        server_env["SKILLPORT_DB_PATH"] = db_path
        embedding_provider = os.environ.get("SKILLPORT_EMBEDDING_PROVIDER", "local")
        server_env["SKILLPORT_EMBEDDING_PROVIDER"] = embedding_provider
        if embedding_provider != "none":
            for key in (
                "SKILLPORT_EMBEDDING_BASE_URL",
                "SKILLPORT_EMBEDDING_MODEL",
                "SKILLPORT_EMBEDDING_API_KEY",
            ):
                value = os.environ.get(key)
                if value:
                    server_env[key] = value
        server_env["SKILLPORT_LOG_LEVEL"] = "ERROR"  # Reduce noise

        # Define server parameters (stdio = Local mode)
        # For Remote mode, use: skillport serve --http
        server_params = StdioServerParameters(
            command="uv", args=["run", "skillport"], env=server_env
        )

        print("Starting SkillPort MCP Client Verification (stdio/Local mode)...")
        print("Note: For HTTP/Remote mode, run: skillport serve --http")
        if embedding_provider != "none":
            print(f"Embedding provider: {embedding_provider}")
            base_url = server_env.get("SKILLPORT_EMBEDDING_BASE_URL", "")
            model = server_env.get("SKILLPORT_EMBEDDING_MODEL", "")
            print(f"Embedding base URL: {base_url}")
            print(f"Embedding model: {model}")
        print()

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # 1. Initialize
                await session.initialize()
                print("[OK] MCP Initialized")

                # 2. List Tools
                tools = await session.list_tools()
                tool_names = [t.name for t in tools.tools]
                print(f"[OK] Found Tools: {tool_names}")

                # In Local mode (stdio), only core tools are available
                # read_skill_file is only available in Remote mode (HTTP)
                expected_tools = ["search_skills", "load_skill"]
                missing = [t for t in expected_tools if t not in tool_names]
                if missing:
                    print(f"[FAIL] Missing core tools: {missing}")
                    return

                # Verify we're in Local mode (no read_skill_file)
                if "read_skill_file" in tool_names:
                    print("[WARN] Unexpected: read_skill_file available in stdio mode")
                else:
                    print("[OK] Mode: Local (stdio) - read_skill_file not available as expected")

                # 3. Test search_skills
                print("\n--- Testing search_skills ---")
                search_result = await session.call_tool(
                    "search_skills", arguments={"query": "hello"}
                )
                print(f"Search Result: {search_result.content[0].text}")

                # 4. Test load_skill
                print("\n--- Testing load_skill ---")
                try:
                    load_result = await session.call_tool(
                        "load_skill", arguments={"skill_id": "hello-world"}
                    )
                    print(f"Load Result: {load_result.content[0].text[:100]}...")
                except Exception as e:
                    print(f"[FAIL] load_skill failed: {e}")
                    return

                # 5. read_skill_file - only available in HTTP mode
                print("\n--- read_skill_file ---")
                print("[INFO] Not available in Local mode (use --http for Remote mode)")

                print("\n[OK] Verification Complete!")


if __name__ == "__main__":
    asyncio.run(run_test())
