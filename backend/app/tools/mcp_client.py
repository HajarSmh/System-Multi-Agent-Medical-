from langchain_mcp_adapters.client import MultiServerMCPClient

# URL du serveur MCP
MCP_SERVER_URL = "http://localhost:24000/mcp"

async def get_mcp_tools() -> list:
    """
    Se connecte au serveur MCP (FastMCP, transport streamable-http)
    et retourne la liste des tools LangChain utilisables dans le graphe.

    Utilisation typique dans graph.py :
        tools = await get_mcp_tools()
        agent = create_react_agent(model=llm, tools=tools + [ask_patient, ...])
    """
    async with MultiServerMCPClient(
        {
            "medical_mcp": {
                "url": MCP_SERVER_URL,
                "transport": "streamable_http",
            }
        }
    ) as client:
        tools = client.get_tools()
        return tools


def get_mcp_tools_sync() -> list:
    """
    Version synchrone pour les contextes non-async (ex: initialisation du graphe).
    """
    import asyncio
    return asyncio.run(get_mcp_tools())