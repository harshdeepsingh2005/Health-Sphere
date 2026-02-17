# MCP Servers Usage Guide

This guide covers how to use all the Model Context Protocol (MCP) servers installed in this workspace for design and development workflows.

## 📁 Directory Structure

```
mcp_servers/
├── mcp-think-tank/           # Enhanced reasoning and memory
├── codearchitect-mcp/        # System design and architecture
├── MiniMax-Coding-Plan-MCP/  # AI-powered search and vision analysis
├── agentic-ai-tool-suite/    # Media, web, and document tools
│   ├── media-tools-server/
│   ├── information-retrieval-server/
│   ├── presentation-creator-server/
│   └── pdf-creator-server/
└── laravel-loop/             # Laravel application integration
```

## 🚀 Quick Start Configuration

### Claude Desktop Configuration

Add to your `claude_desktop_config.json` file:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "think-tank": {
      "command": "node",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/mcp-think-tank/build/index.js"]
    },
    "codearchitect": {
      "command": "node",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/codearchitect-mcp/build/index.js"]
    },
    "minimax-coding-plan": {
      "command": "python",
      "args": ["-m", "minimax_mcp.server"],
      "cwd": "/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/MiniMax-Coding-Plan-MCP",
      "env": {
        "MINIMAX_API_KEY": "your-minimax-api-key",
        "MINIMAX_GROUP_ID": "your-group-id"
      }
    },
    "media-tools": {
      "command": "node",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/agentic-ai-tool-suite/media-tools-server/build/index.js"],
      "env": {
        "UNSPLASH_ACCESS_KEY": "your-unsplash-api-key",
        "GEMINI_API_KEY": "your-gemini-api-key"
      }
    },
    "information-retrieval": {
      "command": "node",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/agentic-ai-tool-suite/information-retrieval-server/build/index.js"],
      "env": {
        "GOOGLE_API_KEY": "your-google-api-key",
        "GOOGLE_CSE_ID": "your-custom-search-engine-id"
      }
    },
    "presentation-creator": {
      "command": "node",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/agentic-ai-tool-suite/presentation-creator-server/build/index.js"]
    },
    "pdf-creator": {
      "command": "python",
      "args": ["/Users/harsheeepsingh/Documents/GitHub/Health-Sphere/mcp_servers/agentic-ai-tool-suite/pdf-creator-server/pdf_creator_server.py"]
    }
  }
}
```

## 🔧 Individual Server Setup

### 1. MCP Think Tank
**Purpose**: Enhanced reasoning, persistent memory, and responsible tool usage

**Features**:
- Structured reasoning environment
- Session storage and retrieval
- Memory management
- Enhanced decision-making processes

**Usage**:
- No API keys required
- Automatically enhances AI assistant capabilities
- Provides better context retention across sessions

---

### 2. CodeArchitect MCP
**Purpose**: System design and architecture assistance

**Features**:
- System design support
- Architecture planning
- Session storage with TOON format
- Token reduction for large contexts

**Usage**:
- No API keys required
- Helps with software architecture decisions
- Provides design pattern recommendations

---

### 3. MiniMax Coding Plan MCP
**Purpose**: AI-powered search and vision analysis

**Features**:
- Advanced search capabilities
- Vision analysis APIs
- Code development workflows
- Project planning assistance

**Setup**:
1. Get API credentials from [MiniMax Platform](https://platform.minimax.com/)
2. Set environment variables:
   ```bash
   export MINIMAX_API_KEY="your-api-key"
   export MINIMAX_GROUP_ID="your-group-id"
   ```

**Usage**:
- Search and analysis of code repositories
- Visual content analysis
- Project planning and task management

---

### 4. Agentic AI Tool Suite

#### A. Media Tools Server
**Purpose**: Image/video search and media understanding

**Features**:
- Image search via Unsplash API
- Video search via YouTube API
- Image content analysis with Gemini
- Video transcript analysis

**Setup**:
1. **Unsplash API Key**: [Get here](https://unsplash.com/developers)
2. **Google Gemini API Key**: [Get here](https://aistudio.google.com/apikey)

**Usage Examples**:
```
"Search for modern office design images"
"Find videos about UX design principles"
"Analyze this image for design elements"
"Get transcript from this YouTube video"
```

#### B. Information Retrieval Server
**Purpose**: Web search and content crawling

**Features**:
- Google Custom Search integration
- Web page content extraction
- Search result analysis
- Content summarization

**Setup**:
1. **Google API Key**: [Google Cloud Console](https://console.cloud.google.com/)
2. **Custom Search Engine ID**: [Create here](https://programmablesearchengine.google.com/)

**Usage Examples**:
```
"Search for latest web design trends"
"Crawl this website for design inspiration"
"Find articles about mobile-first design"
```

#### C. Presentation Creator Server
**Purpose**: PowerPoint and PDF generation from HTML

**Features**:
- HTML to PowerPoint conversion
- PDF generation from HTML content
- Slide template management
- Automated presentation assembly

**Usage Examples**:
```
"Create a presentation from this HTML content"
"Generate slides for my project proposal"
"Convert this web page to PowerPoint"
```

#### D. PDF Creator Server
**Purpose**: PDF document generation

**Features**:
- HTML to PDF conversion
- Document formatting
- Multi-page support
- Custom styling options

**Usage Examples**:
```
"Generate a PDF report from this HTML"
"Create documentation in PDF format"
"Convert my design specs to PDF"
```

---

### 5. Laravel Loop (PHP/Laravel Integration)
**Purpose**: Laravel application integration with MCP

**Features**:
- Laravel model interaction
- Factory data generation
- Filament admin integration
- Stripe API integration

**Setup** (Once Composer is ready):
```bash
cd mcp_servers/laravel-loop
composer install
```

**Usage**:
- Direct integration with Laravel applications
- Database model operations
- Test data generation
- Admin panel interactions

## 🔑 Required API Keys Summary

| Service | API Key Required | Get From |
|---------|------------------|----------|
| MiniMax Coding Plan | ✅ MiniMax API Key + Group ID | [platform.minimax.com](https://platform.minimax.com/) |
| Media Tools | ✅ Unsplash + Gemini Keys | [Unsplash](https://unsplash.com/developers), [Google AI](https://aistudio.google.com/apikey) |
| Information Retrieval | ✅ Google API + CSE ID | [Google Cloud](https://console.cloud.google.com/), [Programmable Search](https://programmablesearchengine.google.com/) |
| Think Tank | ❌ No keys needed | - |
| CodeArchitect | ❌ No keys needed | - |
| Presentation Creator | ❌ No keys needed | - |
| PDF Creator | ❌ No keys needed | - |
| Laravel Loop | ❌ No keys needed | - |

## 🎯 Design Workflow Use Cases

### 1. **Design Research & Inspiration**
- Use **Information Retrieval** to search for design trends
- Use **Media Tools** to find relevant images and videos
- Use **Think Tank** for structured analysis of findings

### 2. **Project Planning & Architecture**
- Use **CodeArchitect** for system design decisions
- Use **MiniMax Coding Plan** for project planning
- Use **Think Tank** for reasoning through complex decisions

### 3. **Content Creation**
- Use **Presentation Creator** for slide decks
- Use **PDF Creator** for documentation
- Use **Media Tools** for visual content analysis

### 4. **Development Integration**
- Use **Laravel Loop** for backend integration
- Use **MiniMax** for code analysis and vision tasks
- Use **Think Tank** for maintaining context across development sessions

## 🚀 Getting Started Checklist

1. ✅ All MCP servers are installed
2. ⏳ Obtain required API keys (see table above)
3. ⏳ Update `claude_desktop_config.json` with your paths and API keys
4. ⏳ Restart Claude Desktop
5. ⏳ Test each server with simple commands

## 🔧 Troubleshooting

### Common Issues:
1. **"Server not found"**: Check file paths in configuration
2. **"API key invalid"**: Verify environment variables are set correctly  
3. **"Permission denied"**: Ensure executable permissions on built files
4. **"Module not found"**: Verify all dependencies are installed

### Testing Commands:
```
"List available MCP tools"
"Test media search functionality"  
"Search for design inspiration"
"Create a simple presentation"
"Generate a PDF document"
```

## 📚 Additional Resources

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [Claude Desktop MCP Setup Guide](https://claude.ai/docs/mcp)
- Individual server README files in their respective directories

---

**Last Updated**: February 17, 2026  
**Status**: All servers ready except Laravel Loop (pending PHP/Composer installation)