Repository: coleam00/remote-mcp-server-with-auth
Files analyzed: 45

Estimated tokens: 109.1k

Directory structure:
└── coleam00-remote-mcp-server-with-auth/
    ├── README.md
    ├── claude-code-prp-setup.md
    ├── CLAUDE.md
    ├── docker-compose.yml
    ├── LICENSE
    ├── package.json
    ├── setup-database.sh
    ├── tsconfig.json
    ├── vitest.config.js
    ├── worker-configuration.d.ts
    ├── wrangler-simple.jsonc
    ├── wrangler.jsonc
    ├── .dev.vars.example
    ├── .prettierrc
    ├── PRPs/
    │   ├── README.md
    │   ├── plan.md
    │   ├── ai_docs/
    │   │   └── mcp_patterns.md
    │   └── templates/
    │       └── prp_mcp_base.md
    ├── src/
    │   ├── index.ts
    │   ├── index_sentry.ts
    │   ├── simple-math.ts
    │   ├── types.ts
    │   ├── auth/
    │   │   ├── github-handler.ts
    │   │   └── oauth-utils.ts
    │   ├── database/
    │   │   ├── connection.ts
    │   │   ├── security.ts
    │   │   └── utils.ts
    │   └── tools/
    │       ├── database-tools-sentry.ts
    │       ├── database-tools.ts
    │       └── register-tools.ts
    ├── tests/
    │   ├── setup.ts
    │   ├── fixtures/
    │   │   ├── auth.fixtures.ts
    │   │   ├── database.fixtures.ts
    │   │   └── mcp.fixtures.ts
    │   ├── mocks/
    │   │   ├── crypto.mock.ts
    │   │   ├── database.mock.ts
    │   │   ├── github.mock.ts
    │   │   └── oauth.mock.ts
    │   └── unit/
    │       ├── database/
    │       │   ├── security.test.ts
    │       │   └── utils.test.ts
    │       ├── tools/
    │       │   └── database-tools.test.ts
    │       └── utils/
    │           └── response-helpers.test.ts
    └── .claude/
        ├── settings.local.json
        └── commands/
            ├── prp-mcp-create.md
            └── prp-mcp-execute.md


================================================
FILE: README.md
================================================
# Cloudflare Remote PostgreSQL Database MCP Server + GitHub OAuth

This is a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) server that enables you to **chat with your PostgreSQL database**, deployable as a remote MCP server with GitHub OAuth through Cloudflare. This is production ready MCP.

## Key Features

- **🗄️ Database Integration with Lifespan**: Direct PostgreSQL database connection for all MCP tool calls
- **🛠️ Modular, Single Purpose Tools**: Following best practices around MCP tools and their descriptions
- **🔐 Role-Based Access**: GitHub username-based permissions for database write operations
- **📊 Schema Discovery**: Automatic table and column information retrieval
- **🛡️ SQL Injection Protection**: Built-in validation and sanitization
- **📈 Monitoring**: Optional Sentry integration for production monitoring
- **☁️ Cloud Native**: Powered by [Cloudflare Workers](https://developers.cloudflare.com/workers/) for global scale

## Modular Architecture

This MCP server uses a clean, modular architecture that makes it easy to extend and maintain:

- **`src/tools/`** - Individual tool implementations in separate files
- **`registerAllTools()`** - Centralized tool registration system 
- **Extensible Design** - Add new tools by creating files in `tools/` and registering them

This architecture allows you to easily add new database operations, external API integrations, or any other MCP tools while keeping the codebase organized and maintainable.

## Transport Protocols

This MCP server supports both modern and legacy transport protocols:

- **`/mcp` - Streamable HTTP** (recommended): Uses a single endpoint with bidirectional communication, automatic connection upgrades, and better resilience for network interruptions
- **`/sse` - Server-Sent Events** (legacy): Uses separate endpoints for requests/responses, maintained for backward compatibility

For new implementations, use the `/mcp` endpoint as it provides better performance and reliability.

## How It Works

The MCP server provides three main tools for database interaction:

1. **`listTables`** - Get database schema and table information (all authenticated users)
2. **`queryDatabase`** - Execute read-only SQL queries (all authenticated users)  
3. **`executeDatabase`** - Execute write operations like INSERT/UPDATE/DELETE (privileged users only)

**Authentication Flow**: Users authenticate via GitHub OAuth → Server validates permissions → Tools become available based on user's GitHub username.

**Security Model**: 
- All authenticated GitHub users can read data
- Only specific GitHub usernames can write/modify data
- SQL injection protection and query validation built-in

## Simple Example First

Want to see a basic MCP server before diving into the full database implementation? Check out `src/simple-math.ts` - a minimal MCP server with a single `calculate` tool that performs basic math operations (add, subtract, multiply, divide). This example demonstrates the core MCP components: server setup, tool definition with Zod schemas, and dual transport support (`/mcp` and `/sse` endpoints). You can run it locally with `wrangler dev --config wrangler-simple.jsonc` and test at `http://localhost:8789/mcp`.

## Prerequisites

- Node.js installed on your machine
- A Cloudflare account (free tier works)
- A GitHub account for OAuth setup
- A PostgreSQL database (local or hosted)

## Getting Started

### Step 1: Install Wrangler CLI

Install Wrangler globally to manage your Cloudflare Workers:

```bash
npm install -g wrangler
```

### Step 2: Authenticate with Cloudflare

Log in to your Cloudflare account:

```bash
wrangler login
```

This will open a browser window where you can authenticate with your Cloudflare account.

### Step 3: Clone and Setup

Clone the repo directly & install dependencies: `npm install`.

## Environment Variables Setup

Before running the MCP server, you need to configure several environment variables for authentication and database access.

### Create Environment Variables File

1. **Create your `.dev.vars` file** from the example:
   ```bash
   cp .dev.vars.example .dev.vars
   ```

2. **Configure all required environment variables** in `.dev.vars`:
   ```
   # GitHub OAuth (for authentication)
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   COOKIE_ENCRYPTION_KEY=your_random_encryption_key

   # Database Connection
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name

   # Optional: Sentry monitoring
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   NODE_ENV=development
   ```

### Getting GitHub OAuth Credentials

1. **Create a GitHub OAuth App** for local development:
   - Go to [GitHub Developer Settings](https://github.com/settings/developers)
   - Click "New OAuth App"
   - **Application name**: `MCP Server (Local Development)`
   - **Homepage URL**: `http://localhost:8792`
   - **Authorization callback URL**: `http://localhost:8792/callback`
   - Click "Register application"

2. **Copy your credentials**:
   - Copy the **Client ID** and paste it as `GITHUB_CLIENT_ID` in `.dev.vars`
   - Click "Generate a new client secret", copy it, and paste as `GITHUB_CLIENT_SECRET` in `.dev.vars`

### Generate Encryption Key

Generate a secure random encryption key for cookie encryption:
```bash
openssl rand -hex 32
```
Copy the output and paste it as `COOKIE_ENCRYPTION_KEY` in `.dev.vars`.

## Database Setup

1. **Set up PostgreSQL** using a hosted service like:
   - [Supabase](https://supabase.com/) (recommended for beginners)
   - [Neon](https://neon.tech/)
   - Or use local PostgreSQL/Supabase

2. **Update the DATABASE_URL** in `.dev.vars` with your connection string:
   ```
   DATABASE_URL=postgresql://username:password@host:5432/database_name
   ```

#### Connection String Examples:
- **Local**: `postgresql://myuser:mypass@localhost:5432/mydb`
- **Supabase**: `postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres`

### Database Schema Setup

The MCP server works with any PostgreSQL database schema. It will automatically discover:
- All tables in the `public` schema
- Column names, types, and constraints
- Primary keys and indexes

**Testing the Connection**: Once you have your database set up, you can test it by asking the MCP server "What tables are available in the database?" and then querying those tables to explore your data.

## Local Development & Testing

**Run the server locally**:
   ```bash
   wrangler dev
   ```
   This makes the server available at `http://localhost:8792`

### Testing with MCP Inspector

Use the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to test your server:

1. **Install and run Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector@latest
   ```

2. **Connect to your local server**:
   - **Preferred**: Enter URL: `http://localhost:8792/mcp` (streamable HTTP transport - newer, more robust)
   - **Alternative**: Enter URL: `http://localhost:8792/sse` (SSE transport - legacy support)
   - Click "Connect"
   - Follow the OAuth prompts to authenticate with GitHub
   - Once connected, you'll see the available tools

3. **Test the tools**:
   - Use `listTables` to see your database structure
   - Use `queryDatabase` to run SELECT queries
   - Use `executeDatabase` (if you have write access) for INSERT/UPDATE/DELETE operations

## Production Deployment

#### Set up a KV namespace
- Create the KV namespace: 
`wrangler kv namespace create "OAUTH_KV"`
- Update the `wrangler.jsonc` file with the KV ID (replace <Add-KV-ID>)

#### Deploy
Deploy the MCP server to make it available on your workers.dev domain

```bash
wrangler deploy
```

### Create environment variables in production
Create a new [GitHub OAuth App](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app): 
- For the Homepage URL, specify `https://mcp-github-oauth.<your-subdomain>.workers.dev`
- For the Authorization callback URL, specify `https://mcp-github-oauth.<your-subdomain>.workers.dev/callback`
- Note your Client ID and generate a Client secret. 
- Set all required secrets via Wrangler:
```bash
wrangler secret put GITHUB_CLIENT_ID
wrangler secret put GITHUB_CLIENT_SECRET
wrangler secret put COOKIE_ENCRYPTION_KEY  # use: openssl rand -hex 32
wrangler secret put DATABASE_URL
wrangler secret put SENTRY_DSN  # optional (more on Sentry setup below)
```

#### Test

Test the remote server using [Inspector](https://modelcontextprotocol.io/docs/tools/inspector): 

```
npx @modelcontextprotocol/inspector@latest
```
Enter `https://mcp-github-oauth.<your-subdomain>.workers.dev/mcp` (preferred) or `https://mcp-github-oauth.<your-subdomain>.workers.dev/sse` (legacy) and hit connect. Once you go through the authentication flow, you'll see the Tools working: 

<img width="640" alt="image" src="https://github.com/user-attachments/assets/7973f392-0a9d-4712-b679-6dd23f824287" />

You now have a remote MCP server deployed! 

## Database Tools & Access Control

### Available Tools

#### 1. `listTables` (All Users)
**Purpose**: Discover database schema and structure  
**Access**: All authenticated GitHub users  
**Usage**: Always run this first to understand your database structure

```
Example output:
- Tables: users, products, orders
- Columns: id (integer), name (varchar), created_at (timestamp)
- Constraints and relationships
```

#### 2. `queryDatabase` (All Users) 
**Purpose**: Execute read-only SQL queries  
**Access**: All authenticated GitHub users  
**Restrictions**: Only SELECT statements and read operations allowed

```sql
-- Examples of allowed queries:
SELECT * FROM users WHERE created_at > '2024-01-01';
SELECT COUNT(*) FROM products;
SELECT u.name, o.total FROM users u JOIN orders o ON u.id = o.user_id;
```

#### 3. `executeDatabase` (Privileged Users Only)
**Purpose**: Execute write operations (INSERT, UPDATE, DELETE, DDL)  
**Access**: Restricted to specific GitHub usernames  
**Capabilities**: Full database write access including schema modifications

```sql
-- Examples of allowed operations:
INSERT INTO users (name, email) VALUES ('New User', 'user@example.com');
UPDATE products SET price = 29.99 WHERE id = 1;
DELETE FROM orders WHERE status = 'cancelled';
CREATE TABLE new_table (id SERIAL PRIMARY KEY, data TEXT);
```

### Access Control Configuration

Database write access is controlled by GitHub username in the `ALLOWED_USERNAMES` configuration:

```typescript
// Add GitHub usernames for database write access
const ALLOWED_USERNAMES = new Set([
  'yourusername',    // Replace with your GitHub username
  'teammate1',       // Add team members who need write access
  'database-admin'   // Add other trusted users
]);
```

**To update access permissions**:
1. Edit `src/index.ts` and `src/index_non_sentry.ts`
2. Update the `ALLOWED_USERNAMES` set with GitHub usernames
3. Redeploy the worker: `wrangler deploy`

### Typical Workflow

1. **🔍 Discover**: Use `listTables` to understand database structure
2. **📊 Query**: Use `queryDatabase` to read and analyze data  
3. **✏️ Modify**: Use `executeDatabase` (if you have write access) to make changes

### Security Features

- **SQL Injection Protection**: All queries are validated before execution
- **Operation Type Detection**: Automatic detection of read vs write operations
- **User Context Tracking**: All operations are logged with GitHub user information
- **Connection Pooling**: Efficient database connection management
- **Error Sanitization**: Database errors are cleaned before being returned to users

### Access the remote MCP server from Claude Desktop

Open Claude Desktop and navigate to Settings -> Developer -> Edit Config. This opens the configuration file that controls which MCP servers Claude can access.

Replace the content with the following configuration. Once you restart Claude Desktop, a browser window will open showing your OAuth login page. Complete the authentication flow to grant Claude access to your MCP server. After you grant access, the tools will become available for you to use. 

```
{
  "mcpServers": {
    "math": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://mcp-github-oauth.<your-subdomain>.workers.dev/mcp"
      ]
    }
  }
}
```

Once the Tools (under 🔨) show up in the interface, you can ask Claude to interact with your database. Example commands:

- **"What tables are available in the database?"** → Uses `listTables` tool
- **"Show me all users created in the last 30 days"** → Uses `queryDatabase` tool  
- **"Add a new user named John with email john@example.com"** → Uses `executeDatabase` tool (if you have write access)

### Using Claude and other MCP Clients

When using Claude to connect to your remote MCP server, you may see some error messages. This is because Claude Desktop doesn't yet support remote MCP servers, so it sometimes gets confused. To verify whether the MCP server is connected, hover over the 🔨 icon in the bottom right corner of Claude's interface. You should see your tools available there.

#### Using Cursor and other MCP Clients

To connect Cursor with your MCP server, choose `Type`: "Command" and in the `Command` field, combine the command and args fields into one (e.g. `npx mcp-remote https://<your-worker-name>.<your-subdomain>.workers.dev/sse`).

Note that while Cursor supports HTTP+SSE servers, it doesn't support authentication, so you still need to use `mcp-remote` (and to use a STDIO server, not an HTTP one).

You can connect your MCP server to other MCP clients like Windsurf by opening the client's configuration file, adding the same JSON that was used for the Claude setup, and restarting the MCP client.

## Sentry Integration (Optional)

This project includes optional Sentry integration for comprehensive error tracking, performance monitoring, and distributed tracing. There are two versions available:

- `src/index.ts` - Standard version without Sentry
- `src/index_sentry.ts` - Version with full Sentry integration

### Setting Up Sentry

1. **Create a Sentry Account**: Sign up at [sentry.io](https://sentry.io) if you don't have an account.

2. **Create a New Project**: Create a new project in Sentry and select "Cloudflare Workers" as the platform (search in the top right).

3. **Get Your DSN**: Copy the DSN from your Sentry project settings.

### Using Sentry in Production

To deploy with Sentry monitoring:

1. **Set the Sentry DSN secret**:
   ```bash
   wrangler secret put SENTRY_DSN
   ```
   Enter your Sentry DSN when prompted.

2. **Update your wrangler.toml** to use the Sentry-enabled version:
   ```toml
   main = "src/index_sentry.ts"
   ```

3. **Deploy with Sentry**:
   ```bash
   wrangler deploy
   ```

### Using Sentry in Development

1. **Add Sentry DSN to your `.dev.vars` file**:
   ```
   SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
   NODE_ENV=development
   ```

2. **Run with Sentry enabled**:
   ```bash
   wrangler dev
   ```

### Sentry Features Included

- **Error Tracking**: Automatic capture of all errors with context
- **Performance Monitoring**: Full request tracing with 100% sample rate
- **User Context**: Automatically binds GitHub user information to events
- **Tool Tracing**: Each MCP tool call is traced with parameters
- **Custom Error Handling**: User-friendly error messages with Event IDs
- **Context Enrichment**: Automatic tagging and context for better debugging

## How does it work? 

#### OAuth Provider
The OAuth Provider library serves as a complete OAuth 2.1 server implementation for Cloudflare Workers. It handles the complexities of the OAuth flow, including token issuance, validation, and management. In this project, it plays the dual role of:

- Authenticating MCP clients that connect to your server
- Managing the connection to GitHub's OAuth services
- Securely storing tokens and authentication state in KV storage

#### Durable MCP
Durable MCP extends the base MCP functionality with Cloudflare's Durable Objects, providing:
- Persistent state management for your MCP server
- Secure storage of authentication context between requests
- Access to authenticated user information via `this.props`
- Support for conditional tool availability based on user identity

#### MCP Remote
The MCP Remote library enables your server to expose tools that can be invoked by MCP clients like the Inspector. It:
- Defines the protocol for communication between clients and your server
- Provides a structured way to define tools
- Handles serialization and deserialization of requests and responses
- Maintains the Server-Sent Events (SSE) connection between clients and your server

## Testing

This project includes comprehensive unit tests covering all major functionality:

```bash
npm test        # Run all tests
npm run test:ui # Run tests with UI
```

The test suite covers database security, tool registration, permission handling, and response formatting with proper mocking of external dependencies.



================================================
FILE: claude-code-prp-setup.md
================================================
# Claude Code PRP Setup Documentation

This document explains the comprehensive Product Requirement Prompt (PRP) system setup for MCP (Model Context Protocol) servers that was implemented across three Claude Code sessions.

## Overview

We created a specialized PRP system tailored for building production-ready MCP servers with GitHub OAuth authentication, PostgreSQL database integration, and Cloudflare Workers deployment. This system enables developers to go from concept to deployed MCP server through a single, well-structured PRP execution.

## Session 1: Initial PRP Template Creation

### What Was Created
- **File**: `PRPs/templates/prp_mcp_server.md` (534 lines)
- **Purpose**: A comprehensive PRP template for building production-ready MCP servers

### Key Features
1. **Production-Ready Patterns**: Based on the existing remote-mcp-server-with-auth codebase
2. **Authentication Integration**: GitHub OAuth flow patterns with cookie-based approval
3. **Database Integration**: PostgreSQL connection management with security best practices
4. **Validation Loops**: 6-level validation from syntax checking to production deployment
5. **Tool Development Patterns**: Three patterns (simple, authenticated, database-integrated)

### Template Structure
```
- Context Section: Critical documentation links and common gotchas
- Implementation Blueprint: Step-by-step tasks with code patterns
- Validation Loops: Comprehensive testing at every level
- Tool Patterns: Reusable patterns for MCP tool development
- Integration Points: Cloudflare Workers, OAuth, database connections
```

## Session 2: CLAUDE.md Adaptation

### The Challenge
The original CLAUDE.md file was written for a Python-based MCP builder project using UV package management, but the actual codebase is Node.js/TypeScript using Cloudflare Workers.

### What Was Updated
- **File**: `CLAUDE.md` (completely rewritten, 932 lines)
- **Removed**: All Python/UV references and vertical slice architecture
- **Added**: Node.js/npm/TypeScript patterns and Wrangler CLI documentation

### Key Additions
1. **Wrangler CLI Commands**: Complete reference with real examples
   - Development: `wrangler dev`, `wrangler dev --config`
   - Deployment: `wrangler deploy`, `wrangler deploy --dry-run`
   - Secrets: `wrangler secret put/list/delete`
   - KV Storage: `wrangler kv namespace create/list`
   - Monitoring: `wrangler tail`, `wrangler types`

2. **Project Architecture Documentation**:
   - File structure with TypeScript sources
   - Three MCP server patterns (standard, Sentry-enabled, simple math)
   - Authentication flow architecture
   - Database security implementation

3. **Development Standards**:
   - TypeScript with Zod validation
   - Error handling patterns
   - MCP-compatible response formats
   - Sentry monitoring integration (optional)

## Session 3: Complete PRP System Implementation

### What Was Created

#### 1. Core PRP Commands
- **`.claude/commands/prp-mcp-create.md`** (118 lines)
  - Creates comprehensive MCP server PRPs
  - Deep research methodology
  - Integration with TodoWrite tool
  
- **`.claude/commands/prp-mcp-execute.md`** (261 lines)
  - Executes MCP server PRPs with validation
  - Multi-stage deployment process
  - Production deployment verification

#### 2. AI Documentation Library
- **`PRPs/ai_docs/mcp_patterns.md`** (491 lines)
  - Core MCP development patterns
  - Security best practices
  - Tool/resource/prompt patterns
  
- **`PRPs/ai_docs/cloudflare_workers_setup.md`** (539 lines)
  - Complete deployment guide
  - Environment configuration
  - Troubleshooting common issues
  
- **`PRPs/ai_docs/oauth_integration.md`** (701 lines)
  - GitHub OAuth 2.0 flow
  - Cookie security implementation
  - Permission management patterns

#### 3. MCP-Specific PRP Template
- **`PRPs/templates/prp_mcp_base.md`** (574 lines)
  - Specialized template for MCP servers
  - References all ai_docs
  - Comprehensive validation loops
  - Production-ready patterns

### Validation Results
- 2,700+ lines of documentation created
- All cross-references validated
- Integration with existing codebase patterns confirmed
- Commands follow established PRP conventions

## How the System Works

### 1. Creating an MCP Server PRP
```bash
# Developer runs:
/prp-mcp-create "Build an MCP server for weather data with caching"

# Claude Code:
1. Uses TodoWrite to plan research
2. Analyzes existing codebase patterns
3. Reads PRPs/templates/prp_mcp_base.md
4. Customizes template with specific requirements
5. Includes all necessary context from ai_docs
6. Generates comprehensive PRP document
```

### 2. Executing the MCP Server PRP
```bash
# Developer runs:
/prp-mcp-execute weather-mcp-server.md

# Claude Code:
1. Creates comprehensive todo list
2. Sets up project structure
3. Implements MCP server with tools
4. Adds authentication if required
5. Integrates database if needed
6. Runs validation loops:
   - TypeScript compilation
   - Local testing with wrangler dev
   - MCP Inspector testing
   - OAuth flow verification
   - Production deployment
```

## Key Benefits

1. **Consistency**: Every MCP server follows proven patterns
2. **Security**: Built-in authentication and SQL injection protection
3. **Production-Ready**: Includes monitoring, error handling, and deployment
4. **Comprehensive**: From initial setup to production deployment
5. **Validated**: Multi-level testing ensures quality

## File Structure Created

```
.claude/
├── commands/
│   ├── prp-mcp-create.md      # Creates MCP server PRPs
│   └── prp-mcp-execute.md     # Executes MCP server PRPs

PRPs/
├── templates/
│   ├── prp_base.md            # General PRP template (existing)
│   ├── prp_mcp_server.md      # Session 1 template
│   └── prp_mcp_base.md        # Session 3 template (primary)
└── ai_docs/
    ├── mcp_patterns.md        # Core development patterns
    ├── cloudflare_workers_setup.md  # Deployment guide
    └── oauth_integration.md   # Authentication patterns

CLAUDE.md                      # Adapted implementation guide
```

## Usage Instructions

### For Developers

1. **To create a new MCP server**:
   ```bash
   # Start Claude Code in your project
   claude-code
   
   # Create a PRP for your MCP server
   /prp-mcp-create "Build an MCP server for [your use case]"
   
   # Execute the generated PRP
   /prp-mcp-execute [generated-prp-file.md]
   ```

2. **To understand the patterns**:
   - Read `CLAUDE.md` for implementation patterns
   - Check `PRPs/ai_docs/` for specific topics
   - Review `src/` files for working examples

3. **To deploy to production**:
   ```bash
   # Set up secrets
   wrangler secret put GITHUB_CLIENT_ID
   wrangler secret put GITHUB_CLIENT_SECRET
   wrangler secret put DATABASE_URL
   
   # Deploy
   wrangler deploy
   ```

## Next Steps

1. **Test the System**: Create a sample MCP server using the PRP commands
2. **Iterate on Templates**: Update templates based on real-world usage
3. **Add More Patterns**: Extend ai_docs with additional patterns as discovered
4. **Community Contribution**: Share successful MCP server PRPs as examples

## Technical Details

### PRP Philosophy
- **Context is King**: Every PRP includes comprehensive context
- **Validation-Driven**: Multiple validation loops ensure quality
- **Production-First**: Always consider deployment and monitoring

### MCP Server Architecture
- **Cloudflare Workers**: Serverless runtime with global distribution
- **Durable Objects**: Stateful MCP agent persistence
- **GitHub OAuth**: Secure authentication with permission management
- **PostgreSQL**: Database integration with connection pooling

### Security Considerations
- SQL injection protection via pattern validation
- HMAC-signed cookies for OAuth approval
- Role-based access control for tools
- Error message sanitization

## Conclusion

This PRP system transforms MCP server development from a complex, error-prone process into a streamlined, validated workflow. By leveraging Claude Code's capabilities and the proven patterns from the remote-mcp-server-with-auth codebase, developers can create production-ready MCP servers in under 30 minutes with confidence in security, scalability, and maintainability.


================================================
FILE: CLAUDE.md
================================================
# MCP Server with GitHub OAuth - Implementation Guide

This guide provides implementation patterns and standards for building MCP (Model Context Protocol) servers with GitHub OAuth authentication using Node.js, TypeScript, and Cloudflare Workers. For WHAT to build, see the PRP (Product Requirement Prompt) documents.

## Core Principles

**IMPORTANT: You MUST follow these principles in all code changes and PRP generations:**

### KISS (Keep It Simple, Stupid)

- Simplicity should be a key goal in design
- Choose straightforward solutions over complex ones whenever possible
- Simple solutions are easier to understand, maintain, and debug

### YAGNI (You Aren't Gonna Need It)

- Avoid building functionality on speculation
- Implement features only when they are needed, not when you anticipate they might be useful in the future

### Open/Closed Principle

- Software entities should be open for extension but closed for modification
- Design systems so that new functionality can be added with minimal changes to existing code

## Package Management & Tooling

**CRITICAL: This project uses npm for Node.js package management and Wrangler CLI for Cloudflare Workers development.**

### Essential npm Commands

```bash
# Install dependencies from package.json
npm install

# Add a dependency
npm install package-name

# Add a development dependency
npm install --save-dev package-name

# Remove a package
npm uninstall package-name

# Update dependencies
npm update

# Run scripts defined in package.json
npm run dev
npm run deploy
npm run type-check
```

### Essential Wrangler CLI Commands

**CRITICAL: Use Wrangler CLI for all Cloudflare Workers development, testing, and deployment.**

```bash
# Authentication
wrangler login          # Login to Cloudflare account
wrangler logout         # Logout from Cloudflare
wrangler whoami         # Check current user

# Development & Testing
wrangler dev           # Start local development server (default port 8787)

# Deployment
wrangler deploy        # Deploy Worker to Cloudflare
wrangler deploy --dry-run  # Test deployment without actually deploying

# Configuration & Types
wrangler types         # Generate TypeScript types from Worker configuration
```

## Project Architecture

**IMPORTANT: This is a Cloudflare Workers MCP server with GitHub OAuth authentication for secure database access.**

### Current Project Structure

```
/
├── src/                          # TypeScript source code
│   ├── index.ts                  # Main MCP server (standard)
│   ├── index_sentry.ts          # Sentry-enabled MCP server
│   ├── simple-math.ts           # Basic MCP example (no auth)
│   ├── github-handler.ts        # GitHub OAuth flow implementation
│   ├── database.ts              # PostgreSQL connection & utilities
│   ├── utils.ts                 # OAuth helper functions
│   └── workers-oauth-utils.ts   # Cookie-based approval system
├── PRPs/                        # Product Requirement Prompts
│   ├── README.md
│   └── templates/
│       └── prp_base.md
├── wrangler.jsonc              # Main Cloudflare Workers configuration
├── wrangler-simple.jsonc       # Simple math example configuration
├── package.json                # npm dependencies & scripts
├── tsconfig.json               # TypeScript configuration
├── worker-configuration.d.ts   # Generated Cloudflare types
└── CLAUDE.md                   # This implementation guide
```

### Key File Purposes (ALWAYS ADD NEW FILES HERE)

**Main Implementation Files:**

- `src/index.ts` - Production MCP server with GitHub OAuth + PostgreSQL
- `src/index_sentry.ts` - Same as above with Sentry monitoring integration
- `src/simple-math.ts` - Basic MCP server example (calculator without auth)

**Authentication & Security:**

- `src/github-handler.ts` - Complete GitHub OAuth 2.0 flow
- `src/workers-oauth-utils.ts` - HMAC-signed cookie approval system
- `src/utils.ts` - OAuth token exchange and URL construction helpers

**Database Integration:**

- `src/database.ts` - PostgreSQL connection pooling, SQL validation, security

**Configuration Files:**

- `wrangler.jsonc` - Main Worker config with Durable Objects, KV, AI bindings
- `wrangler-simple.jsonc` - Simple example configuration
- `tsconfig.json` - TypeScript compiler settings for Cloudflare Workers

## Development Commands

### Core Workflow Commands

```bash
# Setup & Dependencies
npm install                  # Install all dependencies
npm install --save-dev @types/package  # Add dev dependency with types

# Development
wrangler dev                # Start local development server
npm run dev                 # Alternative via npm script

# Type Checking & Validation
npm run type-check          # Run TypeScript compiler check
wrangler types              # Generate Cloudflare Worker types
npx tsc --noEmit           # Type check without compiling

# Testing
npx vitest                  # Run unit tests (if configured)

# Code Quality
npx prettier --write .      # Format code
npx eslint src/            # Lint TypeScript code
```

### Environment Configuration

**Environment Variables Setup:**

```bash
# Create .dev.vars file for local development based on .dev.vars.example
cp .dev.vars.example .dev.vars

# Production secrets (via Wrangler)
wrangler secret put GITHUB_CLIENT_ID
wrangler secret put GITHUB_CLIENT_SECRET
wrangler secret put COOKIE_ENCRYPTION_KEY
wrangler secret put DATABASE_URL
wrangler secret put SENTRY_DSN
```

## MCP Development Context

**IMPORTANT: This project builds production-ready MCP servers using Node.js/TypeScript on Cloudflare Workers with GitHub OAuth authentication.**

### MCP Technology Stack

**Core Technologies:**

- **@modelcontextprotocol/sdk** - Official MCP TypeScript SDK
- **agents/mcp** - Cloudflare Workers MCP agent framework
- **workers-mcp** - MCP transport layer for Workers
- **@cloudflare/workers-oauth-provider** - OAuth 2.1 server implementation

**Cloudflare Platform:**

- **Cloudflare Workers** - Serverless runtime (V8 isolates)
- **Durable Objects** - Stateful objects for MCP agent persistence
- **KV Storage** - OAuth state and session management

### MCP Server Architecture

This project implements MCP servers as Cloudflare Workers with three main patterns:

**1. Authenticated Database MCP Server (`src/index.ts`):**

```typescript
export class MyMCP extends McpAgent<Env, Record<string, never>, Props> {
  server = new McpServer({
    name: "PostgreSQL Database MCP Server",
    version: "1.0.0",
  });

  // MCP Tools available based on user permissions
  // - listTables (all users)
  // - queryDatabase (all users, read-only)
  // - executeDatabase (privileged users only)
}
```

**2. Monitored MCP Server (`src/index_sentry.ts`):**

- Same functionality as above with Sentry instrumentation
- Distributed tracing for MCP tool calls
- Error tracking with event IDs
- Performance monitoring

**3. Simple MCP Server (`src/simple-math.ts`):**

- Basic calculator example without authentication
- Demonstrates core MCP patterns
- Useful for learning and testing

### MCP Development Commands

**Local Development & Testing:**

```bash
# Start main MCP server (with OAuth)
wrangler dev                    # Available at http://localhost:8788/mcp

# Start simple MCP server (no auth)
wrangler dev --config wrangler-simple.jsonc  # Port 8789
```

### Claude Desktop Integration

**For Local Development:**

```json
{
  "mcpServers": {
    "database-mcp": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8788/mcp"],
      "env": {}
    }
  }
}
```

**For Production Deployment:**

```json
{
  "mcpServers": {
    "database-mcp": {
      "command": "npx",
      "args": ["mcp-remote", "https://your-worker.workers.dev/mcp"],
      "env": {}
    }
  }
}
```

### MCP Key Concepts for This Project

- **Tools**: Database operations (listTables, queryDatabase, executeDatabase)
- **Authentication**: GitHub OAuth with role-based access control
- **Transport**: Dual support for HTTP (`/mcp`) and SSE (`/sse`) protocols
- **State**: Durable Objects maintain authenticated user context
- **Security**: SQL injection protection, permission validation, error sanitization

## Database Integration & Security

**CRITICAL: This project provides secure PostgreSQL database access through MCP tools with role-based permissions.**

### Database Architecture

**Connection Management (`src/database.ts`):**

```typescript
// Singleton connection pool with Cloudflare Workers limits
export function getDb(databaseUrl: string): postgres.Sql {
  if (!dbInstance) {
    dbInstance = postgres(databaseUrl, {
      max: 5, // Max 5 connections for Workers
      idle_timeout: 20,
      connect_timeout: 10,
      prepare: true, // Enable prepared statements
    });
  }
  return dbInstance;
}

// Connection wrapper with error handling
export async function withDatabase<T>(databaseUrl: string, operation: (db: postgres.Sql) => Promise<T>): Promise<T> {
  const db = getDb(databaseUrl);
  // Execute operation with timing and error handling
}
```

### Security Implementation

**SQL Injection Protection:**

```typescript
export function validateSqlQuery(sql: string): { isValid: boolean; error?: string } {
  const dangerousPatterns = [
    /;\s*drop\s+/i,
    /;\s*delete\s+.*\s+where\s+1\s*=\s*1/i,
    /;\s*truncate\s+/i,
    // ... more patterns
  ];
  // Pattern-based validation for safety
}

export function isWriteOperation(sql: string): boolean {
  const writeKeywords = ["insert", "update", "delete", "create", "drop", "alter"];
  return writeKeywords.some((keyword) => sql.trim().toLowerCase().startsWith(keyword));
}
```

**Access Control (`src/index.ts`):**

```typescript
const ALLOWED_USERNAMES = new Set<string>([
  'coleam00'  // Only these GitHub usernames can execute write operations
]);

// Tool availability based on user permissions
if (ALLOWED_USERNAMES.has(this.props.login)) {
  // Register executeDatabase tool for privileged users
  this.server.tool("executeDatabase", ...);
}
```

### MCP Tools Implementation

**Available Database Tools:**

1. **`listTables`** - Schema discovery (all authenticated users)
2. **`queryDatabase`** - Read-only SQL queries (all authenticated users)
3. **`executeDatabase`** - Write operations (privileged users only)

**Tool Implementation Pattern:**

```typescript
this.server.tool(
  "queryDatabase",
  "Execute a read-only SQL query against the PostgreSQL database.",
  {
    sql: z.string().describe("SQL query - SELECT statements only"),
  },
  async ({ sql }) => {
    try {
      const validation = validateSqlQuery(sql);
      if (!validation.isValid) {
        return { content: [{ type: "text", text: `Invalid SQL: ${validation.error}`, isError: true }] };
      }

      if (isWriteOperation(sql)) {
        return { content: [{ type: "text", text: "Write operations not allowed", isError: true }] };
      }

      return await withDatabase(this.env.DATABASE_URL, async (db) => {
        const results = await db.unsafe(sql);
        return {
          content: [
            {
              type: "text",
              text: `**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\``,
            },
          ],
        };
      });
    } catch (error) {
      return { content: [{ type: "text", text: `Error: ${formatDatabaseError(error)}`, isError: true }] };
    }
  },
);
```

## GitHub OAuth Implementation

**CRITICAL: This project implements secure GitHub OAuth 2.0 flow with signed cookie-based approval system.**

### OAuth Flow Architecture

**Authentication Flow (`src/github-handler.ts`):**

```typescript
// 1. Authorization Request
app.get("/authorize", async (c) => {
  const oauthReqInfo = await c.env.OAUTH_PROVIDER.parseAuthRequest(c.req.raw);

  // Check if client already approved via signed cookie
  if (await clientIdAlreadyApproved(c.req.raw, oauthReqInfo.clientId, c.env.COOKIE_ENCRYPTION_KEY)) {
    return redirectToGithub(c.req.raw, oauthReqInfo, c.env, {});
  }

  // Show approval dialog
  return renderApprovalDialog(c.req.raw, { client, server, state });
});

// 2. GitHub Callback
app.get("/callback", async (c) => {
  // Exchange code for access token
  const [accessToken, errResponse] = await fetchUpstreamAuthToken({
    client_id: c.env.GITHUB_CLIENT_ID,
    client_secret: c.env.GITHUB_CLIENT_SECRET,
    code: c.req.query("code"),
    redirect_uri: new URL("/callback", c.req.url).href,
  });

  // Get GitHub user info
  const user = await new Octokit({ auth: accessToken }).rest.users.getAuthenticated();

  // Complete authorization with user props
  return c.env.OAUTH_PROVIDER.completeAuthorization({
    props: { accessToken, email, login, name } as Props,
    userId: login,
  });
});
```

### Cookie Security System

**HMAC-Signed Approval Cookies (`src/workers-oauth-utils.ts`):**

```typescript
// Generate signed cookie for client approval
async function signData(key: CryptoKey, data: string): Promise<string> {
  const signatureBuffer = await crypto.subtle.sign("HMAC", key, enc.encode(data));
  return Array.from(new Uint8Array(signatureBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

// Verify cookie integrity
async function verifySignature(key: CryptoKey, signatureHex: string, data: string): Promise<boolean> {
  const signatureBytes = new Uint8Array(signatureHex.match(/.{1,2}/g)!.map((byte) => parseInt(byte, 16)));
  return await crypto.subtle.verify("HMAC", key, signatureBytes.buffer, enc.encode(data));
}
```

### User Context & Permissions

**Authenticated User Props:**

```typescript
type Props = {
  login: string; // GitHub username
  name: string; // Display name
  email: string; // Email address
  accessToken: string; // GitHub access token
};

// Available in MCP tools via this.props
class MyMCP extends McpAgent<Env, Record<string, never>, Props> {
  async init() {
    // Access user context in any tool
    const username = this.props.login;
    const hasWriteAccess = ALLOWED_USERNAMES.has(username);
  }
}
```

## Monitoring & Observability

**CRITICAL: This project supports optional Sentry integration for production monitoring and includes built-in console logging.**

### Logging Architecture

**Two Deployment Options:**

1. **Standard Version (`src/index.ts`)**: Console logging only
2. **Sentry Version (`src/index_sentry.ts`)**: Full Sentry instrumentation

### Sentry Integration (Optional)

**Enable Sentry Monitoring:**

```typescript
// src/index_sentry.ts - Production-ready with monitoring
import * as Sentry from "@sentry/cloudflare";

// Sentry configuration
function getSentryConfig(env: Env) {
  return {
    dsn: env.SENTRY_DSN,
    tracesSampleRate: 1,  // 100% trace sampling
  };
}

// Instrument MCP tools with tracing
private registerTool(name: string, description: string, schema: any, handler: any) {
  this.server.tool(name, description, schema, async (args: any) => {
    return await Sentry.startNewTrace(async () => {
      return await Sentry.startSpan({
        name: `mcp.tool/${name}`,
        attributes: extractMcpParameters(args),
      }, async (span) => {
        // Set user context
        Sentry.setUser({
          username: this.props.login,
          email: this.props.email,
        });

        try {
          return await handler(args);
        } catch (error) {
          span.setStatus({ code: 2 }); // error
          return handleError(error);  // Returns user-friendly error with event ID
        }
      });
    });
  });
}
```

**Sentry Features Enabled:**

- **Error Tracking**: Automatic exception capture with context
- **Performance Monitoring**: Full request tracing with 100% sample rate
- **User Context**: GitHub user information bound to events
- **Tool Tracing**: Each MCP tool call traced with parameters
- **Distributed Tracing**: Request flow across Cloudflare Workers

### Production Logging Patterns

**Console Logging (Standard):**

```typescript
// Database operations
console.log(`Database operation completed successfully in ${duration}ms`);
console.error(`Database operation failed after ${duration}ms:`, error);

// Authentication events
console.log(`User authenticated: ${this.props.login} (${this.props.name})`);

// Tool execution
console.log(`Tool called: ${toolName} by ${this.props.login}`);
console.error(`Tool failed: ${toolName}`, error);
```

**Structured Error Handling:**

```typescript
// Error sanitization for security
export function formatDatabaseError(error: unknown): string {
  if (error instanceof Error) {
    if (error.message.includes("password")) {
      return "Database authentication failed. Please check credentials.";
    }
    if (error.message.includes("timeout")) {
      return "Database connection timed out. Please try again.";
    }
    return `Database error: ${error.message}`;
  }
  return "Unknown database error occurred.";
}
```

### Monitoring Configuration

**Development Monitoring:**

```bash
# Enable Sentry in development
echo 'SENTRY_DSN=https://your-dsn@sentry.io/project' >> .dev.vars
echo 'NODE_ENV=development' >> .dev.vars

# Use Sentry-enabled version
wrangler dev --config wrangler.jsonc  # Ensure main = "src/index_sentry.ts"
```

**Production Monitoring:**

```bash
# Set production secrets
wrangler secret put SENTRY_DSN
wrangler secret put NODE_ENV  # Set to "production"

# Deploy with monitoring
wrangler deploy
```

## TypeScript Development Standards

**CRITICAL: All MCP tools MUST follow TypeScript best practices with Zod validation and proper error handling.**

### Standard Response Format

**ALL tools MUST return MCP-compatible response objects:**

```typescript
import { z } from "zod";

// Tool with proper TypeScript patterns
this.server.tool(
  "standardizedTool",
  "Tool following standard response format",
  {
    name: z.string().min(1, "Name cannot be empty"),
    options: z.object({}).optional(),
  },
  async ({ name, options }) => {
    try {
      // Input already validated by Zod schema
      const result = await processName(name, options);

      // Return standardized success response
      return {
        content: [
          {
            type: "text",
            text: `**Success**\n\nProcessed: ${name}\n\n**Result:**\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\`\n\n**Processing time:** 0.5s`,
          },
        ],
      };
    } catch (error) {
      // Return standardized error response
      return {
        content: [
          {
            type: "text",
            text: `**Error**\n\nProcessing failed: ${error instanceof Error ? error.message : String(error)}`,
            isError: true,
          },
        ],
      };
    }
  },
);
```

### Input Validation with Zod

**ALL tool inputs MUST be validated using Zod schemas:**

```typescript
import { z } from "zod";

// Define validation schemas
const DatabaseQuerySchema = z.object({
  sql: z
    .string()
    .min(1, "SQL query cannot be empty")
    .refine((sql) => sql.trim().toLowerCase().startsWith("select"), {
      message: "Only SELECT queries are allowed",
    }),
  limit: z.number().int().positive().max(1000).optional(),
});

// Use in tool definition
this.server.tool(
  "queryDatabase",
  "Execute a read-only SQL query",
  DatabaseQuerySchema, // Zod schema provides automatic validation
  async ({ sql, limit }) => {
    // sql and limit are already validated and properly typed
    const results = await db.unsafe(sql);
    return { content: [{ type: "text", text: JSON.stringify(results, null, 2) }] };
  },
);
```

### Error Handling Patterns

**Standardized error responses:**

```typescript
// Error handling utility
function createErrorResponse(message: string, details?: any): any {
  return {
    content: [{
      type: "text",
      text: `**Error**\n\n${message}${details ? `\n\n**Details:**\n\`\`\`json\n${JSON.stringify(details, null, 2)}\n\`\`\`` : ''}`,
      isError: true
    }]
  };
}

// Permission error
if (!ALLOWED_USERNAMES.has(this.props.login)) {
  return createErrorResponse(
    "Insufficient permissions for this operation",
    { requiredRole: "privileged", userRole: "standard" }
  );
}

// Validation error
if (isWriteOperation(sql)) {
  return createErrorResponse(
    "Write operations not allowed with this tool",
    { operation: "write", allowedOperations: ["select", "show", "describe"] }
  );
}

// Database error
catch (error) {
  return createErrorResponse(
    "Database operation failed",
    { error: formatDatabaseError(error) }
  );
}
```

### Type Safety Rules

**MANDATORY TypeScript patterns:**

1. **Strict Types**: All parameters and return types explicitly typed
2. **Zod Validation**: All inputs validated with Zod schemas
3. **Error Handling**: All async operations wrapped in try/catch
4. **User Context**: Props typed with GitHub user information
5. **Environment**: Cloudflare Workers types generated with `wrangler types`

## Code Style Preferences

### TypeScript Style

- Use explicit type annotations for all function parameters and return types
- Use JSDoc comments for all exported functions and classes
- Prefer async/await for all asynchronous operations
- **MANDATORY**: Use Zod schemas for all input validation
- **MANDATORY**: Use proper error handling with try/catch blocks
- Keep functions small and focused (single responsibility principle)

### File Organization

- Each MCP server should be self-contained in a single TypeScript file
- Import statements organized: Node.js built-ins, third-party packages, local imports
- Use relative imports within the src/ directory
- **Import Zod for validation and proper types for all modules**

### Testing Conventions

- Use MCP Inspector for integration testing: `npx @modelcontextprotocol/inspector@latest`
- Test with local development server: `wrangler dev`
- Use descriptive tool names and descriptions
- **Test both authentication and permission scenarios**
- **Test input validation with invalid data**

## Important Notes

### What NOT to do

- **NEVER** commit secrets or environment variables to the repository
- **NEVER** build complex solutions when simple ones will work
- **NEVER** skip input validation with Zod schemas

### What TO do

- **ALWAYS** use TypeScript strict mode and proper typing
- **ALWAYS** validate inputs with Zod schemas
- **ALWAYS** follow the core principles (KISS, YAGNI, etc.)
- **ALWAYS** use Wrangler CLI for all development and deployment

## Git Workflow

```bash
# Before committing, always run:
npm run type-check              # Ensure TypeScript compiles
wrangler dev --dry-run          # Test deployment configuration

# Commit with descriptive messages
git add .
git commit -m "feat: add new MCP tool for database queries"
```

## Quick Reference

### Adding a New MCP Tool

1. Add tool to existing MCP server class (`src/index.ts`)
2. Define Zod schema for input validation
3. Implement tool handler with proper error handling
4. Update documentation if needed



================================================
FILE: docker-compose.yml
================================================
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: mcp-cole-pg-test
    restart: always
    environment:
      POSTGRES_USER: mcp_user
      POSTGRES_PASSWORD: mcp_password
      POSTGRES_DB: mcp_database
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mcp_user -d mcp_database"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:


================================================
FILE: LICENSE
================================================
MIT License

Copyright (c) 2025 Cole Medin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



================================================
FILE: package.json
================================================
{
  "name": "remote-mcp-github-oauth",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "deploy": "wrangler deploy",
    "dev": "wrangler dev",
    "start": "wrangler dev",
    "cf-typegen": "wrangler types",
    "type-check": "tsc --noEmit",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:run": "vitest run"
  },
  "dependencies": {
    "@cloudflare/workers-oauth-provider": "^0.0.5",
    "@modelcontextprotocol/sdk": "1.13.1",
    "@sentry/cloudflare": "^9.16.0",
    "agents": "^0.0.100",
    "hono": "^4.8.3",
    "just-pick": "^4.2.0",
    "octokit": "^5.0.3",
    "postgres": "^3.4.5",
    "workers-mcp": "^0.0.13",
    "zod": "^3.25.67"
  },
  "devDependencies": {
    "@cloudflare/vitest-pool-workers": "^0.8.53",
    "@types/node": "^24.0.10",
    "@vitest/ui": "^3.2.4",
    "prettier": "^3.6.2",
    "typescript": "^5.8.3",
    "vi-fetch": "^0.8.0",
    "vitest": "^3.2.4",
    "wrangler": "^4.23.0"
  }
}



================================================
FILE: setup-database.sh
================================================
#!/bin/bash

echo "🚀 Setting up PostgreSQL database for MCP server..."

# Start PostgreSQL container
echo "Starting PostgreSQL container..."
docker compose up -d

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
sleep 5

# Create tables for MCP server
echo "Creating database tables..."
docker exec -i mcp-cole-pg-test psql -U mcp_user -d mcp_database << EOF
-- Create a test table for the MCP server to query
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create a products table for testing
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2),
    stock INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some test data
INSERT INTO users (username, email) VALUES 
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

INSERT INTO products (name, price, stock) VALUES 
    ('Laptop', 999.99, 10),
    ('Mouse', 29.99, 50),
    ('Keyboard', 79.99, 25);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mcp_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mcp_user;
EOF

echo "✅ Database setup complete!"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  Port: 5432"
echo "  Database: mcp_database"
echo "  Username: mcp_user"
echo "  Password: mcp_password"
echo ""
echo "Connection string for .dev.vars:"
echo "DATABASE_URL=postgresql://mcp_user:mcp_password@localhost:5432/mcp_database"


================================================
FILE: tsconfig.json
================================================
{
    "compilerOptions": {
        /* Visit https://aka.ms/tsconfig.json to read more about this file */

        /* Set the JavaScript language version for emitted JavaScript and include compatible library declarations. */
        "target": "es2021",
        /* Specify a set of bundled library declaration files that describe the target runtime environment. */
        "lib": ["es2021"],
        /* Specify what JSX code is generated. */
        "jsx": "react-jsx",

        /* Specify what module code is generated. */
        "module": "es2022",
        /* Specify how TypeScript looks up a file from a given module specifier. */
        "moduleResolution": "bundler",
        /* Specify type package names to be included without being referenced in a source file. */
        "types": [
            "./worker-configuration.d.ts",
            "node"
        ],
        /* Enable importing .json files */
        "resolveJsonModule": true,

        /* Allow JavaScript files to be a part of your program. Use the `checkJS` option to get errors from these files. */
        "allowJs": true,
        /* Enable error reporting in type-checked JavaScript files. */
        "checkJs": false,

        /* Disable emitting files from a compilation. */
        "noEmit": true,

        /* Ensure that each file can be safely transpiled without relying on other imports. */
        "isolatedModules": true,
        /* Allow 'import x from y' when a module doesn't have a default export. */
        "allowSyntheticDefaultImports": true,
        /* Ensure that casing is correct in imports. */
        "forceConsistentCasingInFileNames": true,

        /* Enable all strict type-checking options. */
        "strict": true,

        /* Skip type checking all .d.ts files. */
        "skipLibCheck": true
    },
    "exclude": ["example/**/*"]
}



================================================
FILE: vitest.config.js
================================================
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    environment: 'node',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
  },
})


================================================
FILE: worker-configuration.d.ts
================================================
/* eslint-disable */
// Generated by Wrangler by running `wrangler types` (hash: 8d2a1cc85ea5f1665750373459ceb7e1)
// Runtime types generated with workerd@1.20250709.0 2025-03-10 nodejs_compat
declare namespace Cloudflare {
	interface Env {
		OAUTH_KV: KVNamespace;
		GITHUB_CLIENT_ID: string;
		GITHUB_CLIENT_SECRET: string;
		COOKIE_ENCRYPTION_KEY: string;
		DATABASE_URL: string;
		PERPLEXITY_API_KEY: string;
		ANTHROPIC_API_KEY: string;
		SENTRY_DSN: string;
		NODE_ENV: string;
		MCP_OBJECT: DurableObjectNamespace<import("./src/index").MyMCP>;
		AI: Ai;
	}
}
interface Env extends Cloudflare.Env {}

// Begin runtime types
/*! *****************************************************************************
Copyright (c) Cloudflare. All rights reserved.
Copyright (c) Microsoft Corporation. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at http://www.apache.org/licenses/LICENSE-2.0
THIS CODE IS PROVIDED ON AN *AS IS* BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED
WARRANTIES OR CONDITIONS OF TITLE, FITNESS FOR A PARTICULAR PURPOSE,
MERCHANTABLITY OR NON-INFRINGEMENT.
See the Apache Version 2.0 License for specific language governing permissions
and limitations under the License.
***************************************************************************** */
/* eslint-disable */
// noinspection JSUnusedGlobalSymbols
declare var onmessage: never;
/**
 * An abnormal event (called an exception) which occurs as a result of calling a method or accessing a property of a web API.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/DOMException)
 */
declare class DOMException extends Error {
    constructor(message?: string, name?: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/DOMException/message) */
    readonly message: string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/DOMException/name) */
    readonly name: string;
    /**
     * @deprecated
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/DOMException/code)
     */
    readonly code: number;
    static readonly INDEX_SIZE_ERR: number;
    static readonly DOMSTRING_SIZE_ERR: number;
    static readonly HIERARCHY_REQUEST_ERR: number;
    static readonly WRONG_DOCUMENT_ERR: number;
    static readonly INVALID_CHARACTER_ERR: number;
    static readonly NO_DATA_ALLOWED_ERR: number;
    static readonly NO_MODIFICATION_ALLOWED_ERR: number;
    static readonly NOT_FOUND_ERR: number;
    static readonly NOT_SUPPORTED_ERR: number;
    static readonly INUSE_ATTRIBUTE_ERR: number;
    static readonly INVALID_STATE_ERR: number;
    static readonly SYNTAX_ERR: number;
    static readonly INVALID_MODIFICATION_ERR: number;
    static readonly NAMESPACE_ERR: number;
    static readonly INVALID_ACCESS_ERR: number;
    static readonly VALIDATION_ERR: number;
    static readonly TYPE_MISMATCH_ERR: number;
    static readonly SECURITY_ERR: number;
    static readonly NETWORK_ERR: number;
    static readonly ABORT_ERR: number;
    static readonly URL_MISMATCH_ERR: number;
    static readonly QUOTA_EXCEEDED_ERR: number;
    static readonly TIMEOUT_ERR: number;
    static readonly INVALID_NODE_TYPE_ERR: number;
    static readonly DATA_CLONE_ERR: number;
    get stack(): any;
    set stack(value: any);
}
type WorkerGlobalScopeEventMap = {
    fetch: FetchEvent;
    scheduled: ScheduledEvent;
    queue: QueueEvent;
    unhandledrejection: PromiseRejectionEvent;
    rejectionhandled: PromiseRejectionEvent;
};
declare abstract class WorkerGlobalScope extends EventTarget<WorkerGlobalScopeEventMap> {
    EventTarget: typeof EventTarget;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console) */
interface Console {
    "assert"(condition?: boolean, ...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/clear_static) */
    clear(): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/count_static) */
    count(label?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/countReset_static) */
    countReset(label?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/debug_static) */
    debug(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/dir_static) */
    dir(item?: any, options?: any): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/dirxml_static) */
    dirxml(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/error_static) */
    error(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/group_static) */
    group(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/groupCollapsed_static) */
    groupCollapsed(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/groupEnd_static) */
    groupEnd(): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/info_static) */
    info(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/log_static) */
    log(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/table_static) */
    table(tabularData?: any, properties?: string[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/time_static) */
    time(label?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/timeEnd_static) */
    timeEnd(label?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/timeLog_static) */
    timeLog(label?: string, ...data: any[]): void;
    timeStamp(label?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/trace_static) */
    trace(...data: any[]): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/console/warn_static) */
    warn(...data: any[]): void;
}
declare const console: Console;
type BufferSource = ArrayBufferView | ArrayBuffer;
type TypedArray = Int8Array | Uint8Array | Uint8ClampedArray | Int16Array | Uint16Array | Int32Array | Uint32Array | Float32Array | Float64Array | BigInt64Array | BigUint64Array;
declare namespace WebAssembly {
    class CompileError extends Error {
        constructor(message?: string);
    }
    class RuntimeError extends Error {
        constructor(message?: string);
    }
    type ValueType = "anyfunc" | "externref" | "f32" | "f64" | "i32" | "i64" | "v128";
    interface GlobalDescriptor {
        value: ValueType;
        mutable?: boolean;
    }
    class Global {
        constructor(descriptor: GlobalDescriptor, value?: any);
        value: any;
        valueOf(): any;
    }
    type ImportValue = ExportValue | number;
    type ModuleImports = Record<string, ImportValue>;
    type Imports = Record<string, ModuleImports>;
    type ExportValue = Function | Global | Memory | Table;
    type Exports = Record<string, ExportValue>;
    class Instance {
        constructor(module: Module, imports?: Imports);
        readonly exports: Exports;
    }
    interface MemoryDescriptor {
        initial: number;
        maximum?: number;
        shared?: boolean;
    }
    class Memory {
        constructor(descriptor: MemoryDescriptor);
        readonly buffer: ArrayBuffer;
        grow(delta: number): number;
    }
    type ImportExportKind = "function" | "global" | "memory" | "table";
    interface ModuleExportDescriptor {
        kind: ImportExportKind;
        name: string;
    }
    interface ModuleImportDescriptor {
        kind: ImportExportKind;
        module: string;
        name: string;
    }
    abstract class Module {
        static customSections(module: Module, sectionName: string): ArrayBuffer[];
        static exports(module: Module): ModuleExportDescriptor[];
        static imports(module: Module): ModuleImportDescriptor[];
    }
    type TableKind = "anyfunc" | "externref";
    interface TableDescriptor {
        element: TableKind;
        initial: number;
        maximum?: number;
    }
    class Table {
        constructor(descriptor: TableDescriptor, value?: any);
        readonly length: number;
        get(index: number): any;
        grow(delta: number, value?: any): number;
        set(index: number, value?: any): void;
    }
    function instantiate(module: Module, imports?: Imports): Promise<Instance>;
    function validate(bytes: BufferSource): boolean;
}
/**
 * This ServiceWorker API interface represents the global execution context of a service worker.
 * Available only in secure contexts.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ServiceWorkerGlobalScope)
 */
interface ServiceWorkerGlobalScope extends WorkerGlobalScope {
    DOMException: typeof DOMException;
    WorkerGlobalScope: typeof WorkerGlobalScope;
    btoa(data: string): string;
    atob(data: string): string;
    setTimeout(callback: (...args: any[]) => void, msDelay?: number): number;
    setTimeout<Args extends any[]>(callback: (...args: Args) => void, msDelay?: number, ...args: Args): number;
    clearTimeout(timeoutId: number | null): void;
    setInterval(callback: (...args: any[]) => void, msDelay?: number): number;
    setInterval<Args extends any[]>(callback: (...args: Args) => void, msDelay?: number, ...args: Args): number;
    clearInterval(timeoutId: number | null): void;
    queueMicrotask(task: Function): void;
    structuredClone<T>(value: T, options?: StructuredSerializeOptions): T;
    reportError(error: any): void;
    fetch(input: RequestInfo | URL, init?: RequestInit<RequestInitCfProperties>): Promise<Response>;
    self: ServiceWorkerGlobalScope;
    crypto: Crypto;
    caches: CacheStorage;
    scheduler: Scheduler;
    performance: Performance;
    Cloudflare: Cloudflare;
    readonly origin: string;
    Event: typeof Event;
    ExtendableEvent: typeof ExtendableEvent;
    CustomEvent: typeof CustomEvent;
    PromiseRejectionEvent: typeof PromiseRejectionEvent;
    FetchEvent: typeof FetchEvent;
    TailEvent: typeof TailEvent;
    TraceEvent: typeof TailEvent;
    ScheduledEvent: typeof ScheduledEvent;
    MessageEvent: typeof MessageEvent;
    CloseEvent: typeof CloseEvent;
    ReadableStreamDefaultReader: typeof ReadableStreamDefaultReader;
    ReadableStreamBYOBReader: typeof ReadableStreamBYOBReader;
    ReadableStream: typeof ReadableStream;
    WritableStream: typeof WritableStream;
    WritableStreamDefaultWriter: typeof WritableStreamDefaultWriter;
    TransformStream: typeof TransformStream;
    ByteLengthQueuingStrategy: typeof ByteLengthQueuingStrategy;
    CountQueuingStrategy: typeof CountQueuingStrategy;
    ErrorEvent: typeof ErrorEvent;
    EventSource: typeof EventSource;
    ReadableStreamBYOBRequest: typeof ReadableStreamBYOBRequest;
    ReadableStreamDefaultController: typeof ReadableStreamDefaultController;
    ReadableByteStreamController: typeof ReadableByteStreamController;
    WritableStreamDefaultController: typeof WritableStreamDefaultController;
    TransformStreamDefaultController: typeof TransformStreamDefaultController;
    CompressionStream: typeof CompressionStream;
    DecompressionStream: typeof DecompressionStream;
    TextEncoderStream: typeof TextEncoderStream;
    TextDecoderStream: typeof TextDecoderStream;
    Headers: typeof Headers;
    Body: typeof Body;
    Request: typeof Request;
    Response: typeof Response;
    WebSocket: typeof WebSocket;
    WebSocketPair: typeof WebSocketPair;
    WebSocketRequestResponsePair: typeof WebSocketRequestResponsePair;
    AbortController: typeof AbortController;
    AbortSignal: typeof AbortSignal;
    TextDecoder: typeof TextDecoder;
    TextEncoder: typeof TextEncoder;
    navigator: Navigator;
    Navigator: typeof Navigator;
    URL: typeof URL;
    URLSearchParams: typeof URLSearchParams;
    URLPattern: typeof URLPattern;
    Blob: typeof Blob;
    File: typeof File;
    FormData: typeof FormData;
    Crypto: typeof Crypto;
    SubtleCrypto: typeof SubtleCrypto;
    CryptoKey: typeof CryptoKey;
    CacheStorage: typeof CacheStorage;
    Cache: typeof Cache;
    FixedLengthStream: typeof FixedLengthStream;
    IdentityTransformStream: typeof IdentityTransformStream;
    HTMLRewriter: typeof HTMLRewriter;
}
declare function addEventListener<Type extends keyof WorkerGlobalScopeEventMap>(type: Type, handler: EventListenerOrEventListenerObject<WorkerGlobalScopeEventMap[Type]>, options?: EventTargetAddEventListenerOptions | boolean): void;
declare function removeEventListener<Type extends keyof WorkerGlobalScopeEventMap>(type: Type, handler: EventListenerOrEventListenerObject<WorkerGlobalScopeEventMap[Type]>, options?: EventTargetEventListenerOptions | boolean): void;
/**
 * Dispatches a synthetic event event to target and returns true if either event's cancelable attribute value is false or its preventDefault() method was not invoked, and false otherwise.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventTarget/dispatchEvent)
 */
declare function dispatchEvent(event: WorkerGlobalScopeEventMap[keyof WorkerGlobalScopeEventMap]): boolean;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/btoa) */
declare function btoa(data: string): string;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/atob) */
declare function atob(data: string): string;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/setTimeout) */
declare function setTimeout(callback: (...args: any[]) => void, msDelay?: number): number;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/setTimeout) */
declare function setTimeout<Args extends any[]>(callback: (...args: Args) => void, msDelay?: number, ...args: Args): number;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/clearTimeout) */
declare function clearTimeout(timeoutId: number | null): void;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/setInterval) */
declare function setInterval(callback: (...args: any[]) => void, msDelay?: number): number;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/setInterval) */
declare function setInterval<Args extends any[]>(callback: (...args: Args) => void, msDelay?: number, ...args: Args): number;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/clearInterval) */
declare function clearInterval(timeoutId: number | null): void;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/queueMicrotask) */
declare function queueMicrotask(task: Function): void;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/structuredClone) */
declare function structuredClone<T>(value: T, options?: StructuredSerializeOptions): T;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/reportError) */
declare function reportError(error: any): void;
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Window/fetch) */
declare function fetch(input: RequestInfo | URL, init?: RequestInit<RequestInitCfProperties>): Promise<Response>;
declare const self: ServiceWorkerGlobalScope;
/**
* The Web Crypto API provides a set of low-level functions for common cryptographic tasks.
* The Workers runtime implements the full surface of this API, but with some differences in
* the [supported algorithms](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/#supported-algorithms)
* compared to those implemented in most browsers.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/)
*/
declare const crypto: Crypto;
/**
* The Cache API allows fine grained control of reading and writing from the Cloudflare global network cache.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/)
*/
declare const caches: CacheStorage;
declare const scheduler: Scheduler;
/**
* The Workers runtime supports a subset of the Performance API, used to measure timing and performance,
* as well as timing of subrequests and other operations.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/performance/)
*/
declare const performance: Performance;
declare const Cloudflare: Cloudflare;
declare const origin: string;
declare const navigator: Navigator;
interface TestController {
}
interface ExecutionContext {
    waitUntil(promise: Promise<any>): void;
    passThroughOnException(): void;
    props: any;
}
type ExportedHandlerFetchHandler<Env = unknown, CfHostMetadata = unknown> = (request: Request<CfHostMetadata, IncomingRequestCfProperties<CfHostMetadata>>, env: Env, ctx: ExecutionContext) => Response | Promise<Response>;
type ExportedHandlerTailHandler<Env = unknown> = (events: TraceItem[], env: Env, ctx: ExecutionContext) => void | Promise<void>;
type ExportedHandlerTraceHandler<Env = unknown> = (traces: TraceItem[], env: Env, ctx: ExecutionContext) => void | Promise<void>;
type ExportedHandlerTailStreamHandler<Env = unknown> = (event: TailStream.TailEvent<TailStream.Onset>, env: Env, ctx: ExecutionContext) => TailStream.TailEventHandlerType | Promise<TailStream.TailEventHandlerType>;
type ExportedHandlerScheduledHandler<Env = unknown> = (controller: ScheduledController, env: Env, ctx: ExecutionContext) => void | Promise<void>;
type ExportedHandlerQueueHandler<Env = unknown, Message = unknown> = (batch: MessageBatch<Message>, env: Env, ctx: ExecutionContext) => void | Promise<void>;
type ExportedHandlerTestHandler<Env = unknown> = (controller: TestController, env: Env, ctx: ExecutionContext) => void | Promise<void>;
interface ExportedHandler<Env = unknown, QueueHandlerMessage = unknown, CfHostMetadata = unknown> {
    fetch?: ExportedHandlerFetchHandler<Env, CfHostMetadata>;
    tail?: ExportedHandlerTailHandler<Env>;
    trace?: ExportedHandlerTraceHandler<Env>;
    tailStream?: ExportedHandlerTailStreamHandler<Env>;
    scheduled?: ExportedHandlerScheduledHandler<Env>;
    test?: ExportedHandlerTestHandler<Env>;
    email?: EmailExportedHandler<Env>;
    queue?: ExportedHandlerQueueHandler<Env, QueueHandlerMessage>;
}
interface StructuredSerializeOptions {
    transfer?: any[];
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/PromiseRejectionEvent) */
declare abstract class PromiseRejectionEvent extends Event {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/PromiseRejectionEvent/promise) */
    readonly promise: Promise<any>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/PromiseRejectionEvent/reason) */
    readonly reason: any;
}
declare abstract class Navigator {
    sendBeacon(url: string, body?: (ReadableStream | string | (ArrayBuffer | ArrayBufferView) | Blob | FormData | URLSearchParams | URLSearchParams)): boolean;
    readonly userAgent: string;
    readonly hardwareConcurrency: number;
}
/**
* The Workers runtime supports a subset of the Performance API, used to measure timing and performance,
* as well as timing of subrequests and other operations.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/performance/)
*/
interface Performance {
    /* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/performance/#performancetimeorigin) */
    readonly timeOrigin: number;
    /* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/performance/#performancenow) */
    now(): number;
}
interface AlarmInvocationInfo {
    readonly isRetry: boolean;
    readonly retryCount: number;
}
interface Cloudflare {
    readonly compatibilityFlags: Record<string, boolean>;
}
interface DurableObject {
    fetch(request: Request): Response | Promise<Response>;
    alarm?(alarmInfo?: AlarmInvocationInfo): void | Promise<void>;
    webSocketMessage?(ws: WebSocket, message: string | ArrayBuffer): void | Promise<void>;
    webSocketClose?(ws: WebSocket, code: number, reason: string, wasClean: boolean): void | Promise<void>;
    webSocketError?(ws: WebSocket, error: unknown): void | Promise<void>;
}
type DurableObjectStub<T extends Rpc.DurableObjectBranded | undefined = undefined> = Fetcher<T, "alarm" | "webSocketMessage" | "webSocketClose" | "webSocketError"> & {
    readonly id: DurableObjectId;
    readonly name?: string;
};
interface DurableObjectId {
    toString(): string;
    equals(other: DurableObjectId): boolean;
    readonly name?: string;
}
interface DurableObjectNamespace<T extends Rpc.DurableObjectBranded | undefined = undefined> {
    newUniqueId(options?: DurableObjectNamespaceNewUniqueIdOptions): DurableObjectId;
    idFromName(name: string): DurableObjectId;
    idFromString(id: string): DurableObjectId;
    get(id: DurableObjectId, options?: DurableObjectNamespaceGetDurableObjectOptions): DurableObjectStub<T>;
    jurisdiction(jurisdiction: DurableObjectJurisdiction): DurableObjectNamespace<T>;
}
type DurableObjectJurisdiction = "eu" | "fedramp" | "fedramp-high";
interface DurableObjectNamespaceNewUniqueIdOptions {
    jurisdiction?: DurableObjectJurisdiction;
}
type DurableObjectLocationHint = "wnam" | "enam" | "sam" | "weur" | "eeur" | "apac" | "oc" | "afr" | "me";
interface DurableObjectNamespaceGetDurableObjectOptions {
    locationHint?: DurableObjectLocationHint;
}
interface DurableObjectState {
    waitUntil(promise: Promise<any>): void;
    readonly id: DurableObjectId;
    readonly storage: DurableObjectStorage;
    container?: Container;
    blockConcurrencyWhile<T>(callback: () => Promise<T>): Promise<T>;
    acceptWebSocket(ws: WebSocket, tags?: string[]): void;
    getWebSockets(tag?: string): WebSocket[];
    setWebSocketAutoResponse(maybeReqResp?: WebSocketRequestResponsePair): void;
    getWebSocketAutoResponse(): WebSocketRequestResponsePair | null;
    getWebSocketAutoResponseTimestamp(ws: WebSocket): Date | null;
    setHibernatableWebSocketEventTimeout(timeoutMs?: number): void;
    getHibernatableWebSocketEventTimeout(): number | null;
    getTags(ws: WebSocket): string[];
    abort(reason?: string): void;
}
interface DurableObjectTransaction {
    get<T = unknown>(key: string, options?: DurableObjectGetOptions): Promise<T | undefined>;
    get<T = unknown>(keys: string[], options?: DurableObjectGetOptions): Promise<Map<string, T>>;
    list<T = unknown>(options?: DurableObjectListOptions): Promise<Map<string, T>>;
    put<T>(key: string, value: T, options?: DurableObjectPutOptions): Promise<void>;
    put<T>(entries: Record<string, T>, options?: DurableObjectPutOptions): Promise<void>;
    delete(key: string, options?: DurableObjectPutOptions): Promise<boolean>;
    delete(keys: string[], options?: DurableObjectPutOptions): Promise<number>;
    rollback(): void;
    getAlarm(options?: DurableObjectGetAlarmOptions): Promise<number | null>;
    setAlarm(scheduledTime: number | Date, options?: DurableObjectSetAlarmOptions): Promise<void>;
    deleteAlarm(options?: DurableObjectSetAlarmOptions): Promise<void>;
}
interface DurableObjectStorage {
    get<T = unknown>(key: string, options?: DurableObjectGetOptions): Promise<T | undefined>;
    get<T = unknown>(keys: string[], options?: DurableObjectGetOptions): Promise<Map<string, T>>;
    list<T = unknown>(options?: DurableObjectListOptions): Promise<Map<string, T>>;
    put<T>(key: string, value: T, options?: DurableObjectPutOptions): Promise<void>;
    put<T>(entries: Record<string, T>, options?: DurableObjectPutOptions): Promise<void>;
    delete(key: string, options?: DurableObjectPutOptions): Promise<boolean>;
    delete(keys: string[], options?: DurableObjectPutOptions): Promise<number>;
    deleteAll(options?: DurableObjectPutOptions): Promise<void>;
    transaction<T>(closure: (txn: DurableObjectTransaction) => Promise<T>): Promise<T>;
    getAlarm(options?: DurableObjectGetAlarmOptions): Promise<number | null>;
    setAlarm(scheduledTime: number | Date, options?: DurableObjectSetAlarmOptions): Promise<void>;
    deleteAlarm(options?: DurableObjectSetAlarmOptions): Promise<void>;
    sync(): Promise<void>;
    sql: SqlStorage;
    transactionSync<T>(closure: () => T): T;
    getCurrentBookmark(): Promise<string>;
    getBookmarkForTime(timestamp: number | Date): Promise<string>;
    onNextSessionRestoreBookmark(bookmark: string): Promise<string>;
}
interface DurableObjectListOptions {
    start?: string;
    startAfter?: string;
    end?: string;
    prefix?: string;
    reverse?: boolean;
    limit?: number;
    allowConcurrency?: boolean;
    noCache?: boolean;
}
interface DurableObjectGetOptions {
    allowConcurrency?: boolean;
    noCache?: boolean;
}
interface DurableObjectGetAlarmOptions {
    allowConcurrency?: boolean;
}
interface DurableObjectPutOptions {
    allowConcurrency?: boolean;
    allowUnconfirmed?: boolean;
    noCache?: boolean;
}
interface DurableObjectSetAlarmOptions {
    allowConcurrency?: boolean;
    allowUnconfirmed?: boolean;
}
declare class WebSocketRequestResponsePair {
    constructor(request: string, response: string);
    get request(): string;
    get response(): string;
}
interface AnalyticsEngineDataset {
    writeDataPoint(event?: AnalyticsEngineDataPoint): void;
}
interface AnalyticsEngineDataPoint {
    indexes?: ((ArrayBuffer | string) | null)[];
    doubles?: number[];
    blobs?: ((ArrayBuffer | string) | null)[];
}
/**
 * An event which takes place in the DOM.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event)
 */
declare class Event {
    constructor(type: string, init?: EventInit);
    /**
     * Returns the type of event, e.g. "click", "hashchange", or "submit".
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/type)
     */
    get type(): string;
    /**
     * Returns the event's phase, which is one of NONE, CAPTURING_PHASE, AT_TARGET, and BUBBLING_PHASE.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/eventPhase)
     */
    get eventPhase(): number;
    /**
     * Returns true or false depending on how event was initialized. True if event invokes listeners past a ShadowRoot node that is the root of its target, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/composed)
     */
    get composed(): boolean;
    /**
     * Returns true or false depending on how event was initialized. True if event goes through its target's ancestors in reverse tree order, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/bubbles)
     */
    get bubbles(): boolean;
    /**
     * Returns true or false depending on how event was initialized. Its return value does not always carry meaning, but true can indicate that part of the operation during which event was dispatched, can be canceled by invoking the preventDefault() method.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/cancelable)
     */
    get cancelable(): boolean;
    /**
     * Returns true if preventDefault() was invoked successfully to indicate cancelation, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/defaultPrevented)
     */
    get defaultPrevented(): boolean;
    /**
     * @deprecated
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/returnValue)
     */
    get returnValue(): boolean;
    /**
     * Returns the object whose event listener's callback is currently being invoked.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/currentTarget)
     */
    get currentTarget(): EventTarget | undefined;
    /**
     * Returns the object to which event is dispatched (its target).
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/target)
     */
    get target(): EventTarget | undefined;
    /**
     * @deprecated
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/srcElement)
     */
    get srcElement(): EventTarget | undefined;
    /**
     * Returns the event's timestamp as the number of milliseconds measured relative to the time origin.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/timeStamp)
     */
    get timeStamp(): number;
    /**
     * Returns true if event was dispatched by the user agent, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/isTrusted)
     */
    get isTrusted(): boolean;
    /**
     * @deprecated
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/cancelBubble)
     */
    get cancelBubble(): boolean;
    /**
     * @deprecated
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/cancelBubble)
     */
    set cancelBubble(value: boolean);
    /**
     * Invoking this method prevents event from reaching any registered event listeners after the current one finishes running and, when dispatched in a tree, also prevents event from reaching any other objects.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/stopImmediatePropagation)
     */
    stopImmediatePropagation(): void;
    /**
     * If invoked when the cancelable attribute value is true, and while executing a listener for the event with passive set to false, signals to the operation that caused event to be dispatched that it needs to be canceled.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/preventDefault)
     */
    preventDefault(): void;
    /**
     * When dispatched in a tree, invoking this method prevents event from reaching any objects other than the current object.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/stopPropagation)
     */
    stopPropagation(): void;
    /**
     * Returns the invocation target objects of event's path (objects on which listeners will be invoked), except for any nodes in shadow trees of which the shadow root's mode is "closed" that are not reachable from event's currentTarget.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Event/composedPath)
     */
    composedPath(): EventTarget[];
    static readonly NONE: number;
    static readonly CAPTURING_PHASE: number;
    static readonly AT_TARGET: number;
    static readonly BUBBLING_PHASE: number;
}
interface EventInit {
    bubbles?: boolean;
    cancelable?: boolean;
    composed?: boolean;
}
type EventListener<EventType extends Event = Event> = (event: EventType) => void;
interface EventListenerObject<EventType extends Event = Event> {
    handleEvent(event: EventType): void;
}
type EventListenerOrEventListenerObject<EventType extends Event = Event> = EventListener<EventType> | EventListenerObject<EventType>;
/**
 * EventTarget is a DOM interface implemented by objects that can receive events and may have listeners for them.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventTarget)
 */
declare class EventTarget<EventMap extends Record<string, Event> = Record<string, Event>> {
    constructor();
    /**
     * Appends an event listener for events whose type attribute value is type. The callback argument sets the callback that will be invoked when the event is dispatched.
     *
     * The options argument sets listener-specific options. For compatibility this can be a boolean, in which case the method behaves exactly as if the value was specified as options's capture.
     *
     * When set to true, options's capture prevents callback from being invoked when the event's eventPhase attribute value is BUBBLING_PHASE. When false (or not present), callback will not be invoked when event's eventPhase attribute value is CAPTURING_PHASE. Either way, callback will be invoked if event's eventPhase attribute value is AT_TARGET.
     *
     * When set to true, options's passive indicates that the callback will not cancel the event by invoking preventDefault(). This is used to enable performance optimizations described in § 2.8 Observing event listeners.
     *
     * When set to true, options's once indicates that the callback will only be invoked once after which the event listener will be removed.
     *
     * If an AbortSignal is passed for options's signal, then the event listener will be removed when signal is aborted.
     *
     * The event listener is appended to target's event listener list and is not appended if it has the same type, callback, and capture.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventTarget/addEventListener)
     */
    addEventListener<Type extends keyof EventMap>(type: Type, handler: EventListenerOrEventListenerObject<EventMap[Type]>, options?: EventTargetAddEventListenerOptions | boolean): void;
    /**
     * Removes the event listener in target's event listener list with the same type, callback, and options.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventTarget/removeEventListener)
     */
    removeEventListener<Type extends keyof EventMap>(type: Type, handler: EventListenerOrEventListenerObject<EventMap[Type]>, options?: EventTargetEventListenerOptions | boolean): void;
    /**
     * Dispatches a synthetic event event to target and returns true if either event's cancelable attribute value is false or its preventDefault() method was not invoked, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventTarget/dispatchEvent)
     */
    dispatchEvent(event: EventMap[keyof EventMap]): boolean;
}
interface EventTargetEventListenerOptions {
    capture?: boolean;
}
interface EventTargetAddEventListenerOptions {
    capture?: boolean;
    passive?: boolean;
    once?: boolean;
    signal?: AbortSignal;
}
interface EventTargetHandlerObject {
    handleEvent: (event: Event) => any | undefined;
}
/**
 * A controller object that allows you to abort one or more DOM requests as and when desired.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortController)
 */
declare class AbortController {
    constructor();
    /**
     * Returns the AbortSignal object associated with this object.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortController/signal)
     */
    get signal(): AbortSignal;
    /**
     * Invoking this method will set this object's AbortSignal's aborted flag and signal to any observers that the associated activity is to be aborted.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortController/abort)
     */
    abort(reason?: any): void;
}
/**
 * A signal object that allows you to communicate with a DOM request (such as a Fetch) and abort it if required via an AbortController object.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal)
 */
declare abstract class AbortSignal extends EventTarget {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/abort_static) */
    static abort(reason?: any): AbortSignal;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/timeout_static) */
    static timeout(delay: number): AbortSignal;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/any_static) */
    static any(signals: AbortSignal[]): AbortSignal;
    /**
     * Returns true if this AbortSignal's AbortController has signaled to abort, and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/aborted)
     */
    get aborted(): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/reason) */
    get reason(): any;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/abort_event) */
    get onabort(): any | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/abort_event) */
    set onabort(value: any | null);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/AbortSignal/throwIfAborted) */
    throwIfAborted(): void;
}
interface Scheduler {
    wait(delay: number, maybeOptions?: SchedulerWaitOptions): Promise<void>;
}
interface SchedulerWaitOptions {
    signal?: AbortSignal;
}
/**
 * Extends the lifetime of the install and activate events dispatched on the global scope as part of the service worker lifecycle. This ensures that any functional events (like FetchEvent) are not dispatched until it upgrades database schemas and deletes the outdated cache entries.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ExtendableEvent)
 */
declare abstract class ExtendableEvent extends Event {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ExtendableEvent/waitUntil) */
    waitUntil(promise: Promise<any>): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CustomEvent) */
declare class CustomEvent<T = any> extends Event {
    constructor(type: string, init?: CustomEventCustomEventInit);
    /**
     * Returns any custom data event was created with. Typically used for synthetic events.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CustomEvent/detail)
     */
    get detail(): T;
}
interface CustomEventCustomEventInit {
    bubbles?: boolean;
    cancelable?: boolean;
    composed?: boolean;
    detail?: any;
}
/**
 * A file-like object of immutable, raw data. Blobs represent data that isn't necessarily in a JavaScript-native format. The File interface is based on Blob, inheriting blob functionality and expanding it to support files on the user's system.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob)
 */
declare class Blob {
    constructor(type?: ((ArrayBuffer | ArrayBufferView) | string | Blob)[], options?: BlobOptions);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/size) */
    get size(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/type) */
    get type(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/slice) */
    slice(start?: number, end?: number, type?: string): Blob;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/arrayBuffer) */
    arrayBuffer(): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/bytes) */
    bytes(): Promise<Uint8Array>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/text) */
    text(): Promise<string>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Blob/stream) */
    stream(): ReadableStream;
}
interface BlobOptions {
    type?: string;
}
/**
 * Provides information about files and allows JavaScript in a web page to access their content.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/File)
 */
declare class File extends Blob {
    constructor(bits: ((ArrayBuffer | ArrayBufferView) | string | Blob)[] | undefined, name: string, options?: FileOptions);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/File/name) */
    get name(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/File/lastModified) */
    get lastModified(): number;
}
interface FileOptions {
    type?: string;
    lastModified?: number;
}
/**
* The Cache API allows fine grained control of reading and writing from the Cloudflare global network cache.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/)
*/
declare abstract class CacheStorage {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CacheStorage/open) */
    open(cacheName: string): Promise<Cache>;
    readonly default: Cache;
}
/**
* The Cache API allows fine grained control of reading and writing from the Cloudflare global network cache.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/)
*/
declare abstract class Cache {
    /* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/#delete) */
    delete(request: RequestInfo | URL, options?: CacheQueryOptions): Promise<boolean>;
    /* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/#match) */
    match(request: RequestInfo | URL, options?: CacheQueryOptions): Promise<Response | undefined>;
    /* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/cache/#put) */
    put(request: RequestInfo | URL, response: Response): Promise<void>;
}
interface CacheQueryOptions {
    ignoreMethod?: boolean;
}
/**
* The Web Crypto API provides a set of low-level functions for common cryptographic tasks.
* The Workers runtime implements the full surface of this API, but with some differences in
* the [supported algorithms](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/#supported-algorithms)
* compared to those implemented in most browsers.
*
* [Cloudflare Docs Reference](https://developers.cloudflare.com/workers/runtime-apis/web-crypto/)
*/
declare abstract class Crypto {
    /**
     * Available only in secure contexts.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Crypto/subtle)
     */
    get subtle(): SubtleCrypto;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Crypto/getRandomValues) */
    getRandomValues<T extends Int8Array | Uint8Array | Int16Array | Uint16Array | Int32Array | Uint32Array | BigInt64Array | BigUint64Array>(buffer: T): T;
    /**
     * Available only in secure contexts.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Crypto/randomUUID)
     */
    randomUUID(): string;
    DigestStream: typeof DigestStream;
}
/**
 * This Web Crypto API interface provides a number of low-level cryptographic functions. It is accessed via the Crypto.subtle properties available in a window context (via Window.crypto).
 * Available only in secure contexts.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto)
 */
declare abstract class SubtleCrypto {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/encrypt) */
    encrypt(algorithm: string | SubtleCryptoEncryptAlgorithm, key: CryptoKey, plainText: ArrayBuffer | ArrayBufferView): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/decrypt) */
    decrypt(algorithm: string | SubtleCryptoEncryptAlgorithm, key: CryptoKey, cipherText: ArrayBuffer | ArrayBufferView): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/sign) */
    sign(algorithm: string | SubtleCryptoSignAlgorithm, key: CryptoKey, data: ArrayBuffer | ArrayBufferView): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/verify) */
    verify(algorithm: string | SubtleCryptoSignAlgorithm, key: CryptoKey, signature: ArrayBuffer | ArrayBufferView, data: ArrayBuffer | ArrayBufferView): Promise<boolean>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/digest) */
    digest(algorithm: string | SubtleCryptoHashAlgorithm, data: ArrayBuffer | ArrayBufferView): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/generateKey) */
    generateKey(algorithm: string | SubtleCryptoGenerateKeyAlgorithm, extractable: boolean, keyUsages: string[]): Promise<CryptoKey | CryptoKeyPair>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/deriveKey) */
    deriveKey(algorithm: string | SubtleCryptoDeriveKeyAlgorithm, baseKey: CryptoKey, derivedKeyAlgorithm: string | SubtleCryptoImportKeyAlgorithm, extractable: boolean, keyUsages: string[]): Promise<CryptoKey>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/deriveBits) */
    deriveBits(algorithm: string | SubtleCryptoDeriveKeyAlgorithm, baseKey: CryptoKey, length?: number | null): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/importKey) */
    importKey(format: string, keyData: (ArrayBuffer | ArrayBufferView) | JsonWebKey, algorithm: string | SubtleCryptoImportKeyAlgorithm, extractable: boolean, keyUsages: string[]): Promise<CryptoKey>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/exportKey) */
    exportKey(format: string, key: CryptoKey): Promise<ArrayBuffer | JsonWebKey>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/wrapKey) */
    wrapKey(format: string, key: CryptoKey, wrappingKey: CryptoKey, wrapAlgorithm: string | SubtleCryptoEncryptAlgorithm): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/SubtleCrypto/unwrapKey) */
    unwrapKey(format: string, wrappedKey: ArrayBuffer | ArrayBufferView, unwrappingKey: CryptoKey, unwrapAlgorithm: string | SubtleCryptoEncryptAlgorithm, unwrappedKeyAlgorithm: string | SubtleCryptoImportKeyAlgorithm, extractable: boolean, keyUsages: string[]): Promise<CryptoKey>;
    timingSafeEqual(a: ArrayBuffer | ArrayBufferView, b: ArrayBuffer | ArrayBufferView): boolean;
}
/**
 * The CryptoKey dictionary of the Web Crypto API represents a cryptographic key.
 * Available only in secure contexts.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CryptoKey)
 */
declare abstract class CryptoKey {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CryptoKey/type) */
    readonly type: string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CryptoKey/extractable) */
    readonly extractable: boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CryptoKey/algorithm) */
    readonly algorithm: CryptoKeyKeyAlgorithm | CryptoKeyAesKeyAlgorithm | CryptoKeyHmacKeyAlgorithm | CryptoKeyRsaKeyAlgorithm | CryptoKeyEllipticKeyAlgorithm | CryptoKeyArbitraryKeyAlgorithm;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CryptoKey/usages) */
    readonly usages: string[];
}
interface CryptoKeyPair {
    publicKey: CryptoKey;
    privateKey: CryptoKey;
}
interface JsonWebKey {
    kty: string;
    use?: string;
    key_ops?: string[];
    alg?: string;
    ext?: boolean;
    crv?: string;
    x?: string;
    y?: string;
    d?: string;
    n?: string;
    e?: string;
    p?: string;
    q?: string;
    dp?: string;
    dq?: string;
    qi?: string;
    oth?: RsaOtherPrimesInfo[];
    k?: string;
}
interface RsaOtherPrimesInfo {
    r?: string;
    d?: string;
    t?: string;
}
interface SubtleCryptoDeriveKeyAlgorithm {
    name: string;
    salt?: (ArrayBuffer | ArrayBufferView);
    iterations?: number;
    hash?: (string | SubtleCryptoHashAlgorithm);
    $public?: CryptoKey;
    info?: (ArrayBuffer | ArrayBufferView);
}
interface SubtleCryptoEncryptAlgorithm {
    name: string;
    iv?: (ArrayBuffer | ArrayBufferView);
    additionalData?: (ArrayBuffer | ArrayBufferView);
    tagLength?: number;
    counter?: (ArrayBuffer | ArrayBufferView);
    length?: number;
    label?: (ArrayBuffer | ArrayBufferView);
}
interface SubtleCryptoGenerateKeyAlgorithm {
    name: string;
    hash?: (string | SubtleCryptoHashAlgorithm);
    modulusLength?: number;
    publicExponent?: (ArrayBuffer | ArrayBufferView);
    length?: number;
    namedCurve?: string;
}
interface SubtleCryptoHashAlgorithm {
    name: string;
}
interface SubtleCryptoImportKeyAlgorithm {
    name: string;
    hash?: (string | SubtleCryptoHashAlgorithm);
    length?: number;
    namedCurve?: string;
    compressed?: boolean;
}
interface SubtleCryptoSignAlgorithm {
    name: string;
    hash?: (string | SubtleCryptoHashAlgorithm);
    dataLength?: number;
    saltLength?: number;
}
interface CryptoKeyKeyAlgorithm {
    name: string;
}
interface CryptoKeyAesKeyAlgorithm {
    name: string;
    length: number;
}
interface CryptoKeyHmacKeyAlgorithm {
    name: string;
    hash: CryptoKeyKeyAlgorithm;
    length: number;
}
interface CryptoKeyRsaKeyAlgorithm {
    name: string;
    modulusLength: number;
    publicExponent: ArrayBuffer | ArrayBufferView;
    hash?: CryptoKeyKeyAlgorithm;
}
interface CryptoKeyEllipticKeyAlgorithm {
    name: string;
    namedCurve: string;
}
interface CryptoKeyArbitraryKeyAlgorithm {
    name: string;
    hash?: CryptoKeyKeyAlgorithm;
    namedCurve?: string;
    length?: number;
}
declare class DigestStream extends WritableStream<ArrayBuffer | ArrayBufferView> {
    constructor(algorithm: string | SubtleCryptoHashAlgorithm);
    readonly digest: Promise<ArrayBuffer>;
    get bytesWritten(): number | bigint;
}
/**
 * A decoder for a specific method, that is a specific character encoding, like utf-8, iso-8859-2, koi8, cp1261, gbk, etc. A decoder takes a stream of bytes as input and emits a stream of code points. For a more scalable, non-native library, see StringView – a C-like representation of strings based on typed arrays.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextDecoder)
 */
declare class TextDecoder {
    constructor(label?: string, options?: TextDecoderConstructorOptions);
    /**
     * Returns the result of running encoding's decoder. The method can be invoked zero or more times with options's stream set to true, and then once without options's stream (or set to false), to process a fragmented input. If the invocation without options's stream (or set to false) has no input, it's clearest to omit both arguments.
     *
     * ```
     * var string = "", decoder = new TextDecoder(encoding), buffer;
     * while(buffer = next_chunk()) {
     *   string += decoder.decode(buffer, {stream:true});
     * }
     * string += decoder.decode(); // end-of-queue
     * ```
     *
     * If the error mode is "fatal" and encoding's decoder returns error, throws a TypeError.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextDecoder/decode)
     */
    decode(input?: (ArrayBuffer | ArrayBufferView), options?: TextDecoderDecodeOptions): string;
    get encoding(): string;
    get fatal(): boolean;
    get ignoreBOM(): boolean;
}
/**
 * TextEncoder takes a stream of code points as input and emits a stream of bytes. For a more scalable, non-native library, see StringView – a C-like representation of strings based on typed arrays.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextEncoder)
 */
declare class TextEncoder {
    constructor();
    /**
     * Returns the result of running UTF-8's encoder.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextEncoder/encode)
     */
    encode(input?: string): Uint8Array;
    /**
     * Runs the UTF-8 encoder on source, stores the result of that operation into destination, and returns the progress made as an object wherein read is the number of converted code units of source and written is the number of bytes modified in destination.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextEncoder/encodeInto)
     */
    encodeInto(input: string, buffer: ArrayBuffer | ArrayBufferView): TextEncoderEncodeIntoResult;
    get encoding(): string;
}
interface TextDecoderConstructorOptions {
    fatal: boolean;
    ignoreBOM: boolean;
}
interface TextDecoderDecodeOptions {
    stream: boolean;
}
interface TextEncoderEncodeIntoResult {
    read: number;
    written: number;
}
/**
 * Events providing information related to errors in scripts or in files.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent)
 */
declare class ErrorEvent extends Event {
    constructor(type: string, init?: ErrorEventErrorEventInit);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent/filename) */
    get filename(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent/message) */
    get message(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent/lineno) */
    get lineno(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent/colno) */
    get colno(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ErrorEvent/error) */
    get error(): any;
}
interface ErrorEventErrorEventInit {
    message?: string;
    filename?: string;
    lineno?: number;
    colno?: number;
    error?: any;
}
/**
 * Provides a way to easily construct a set of key/value pairs representing form fields and their values, which can then be easily sent using the XMLHttpRequest.send() method. It uses the same format a form would use if the encoding type were set to "multipart/form-data".
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData)
 */
declare class FormData {
    constructor();
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/append) */
    append(name: string, value: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/append) */
    append(name: string, value: Blob, filename?: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/delete) */
    delete(name: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/get) */
    get(name: string): (File | string) | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/getAll) */
    getAll(name: string): (File | string)[];
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/has) */
    has(name: string): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/set) */
    set(name: string, value: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FormData/set) */
    set(name: string, value: Blob, filename?: string): void;
    /* Returns an array of key, value pairs for every entry in the list. */
    entries(): IterableIterator<[
        key: string,
        value: File | string
    ]>;
    /* Returns a list of keys in the list. */
    keys(): IterableIterator<string>;
    /* Returns a list of values in the list. */
    values(): IterableIterator<(File | string)>;
    forEach<This = unknown>(callback: (this: This, value: File | string, key: string, parent: FormData) => void, thisArg?: This): void;
    [Symbol.iterator](): IterableIterator<[
        key: string,
        value: File | string
    ]>;
}
interface ContentOptions {
    html?: boolean;
}
declare class HTMLRewriter {
    constructor();
    on(selector: string, handlers: HTMLRewriterElementContentHandlers): HTMLRewriter;
    onDocument(handlers: HTMLRewriterDocumentContentHandlers): HTMLRewriter;
    transform(response: Response): Response;
}
interface HTMLRewriterElementContentHandlers {
    element?(element: Element): void | Promise<void>;
    comments?(comment: Comment): void | Promise<void>;
    text?(element: Text): void | Promise<void>;
}
interface HTMLRewriterDocumentContentHandlers {
    doctype?(doctype: Doctype): void | Promise<void>;
    comments?(comment: Comment): void | Promise<void>;
    text?(text: Text): void | Promise<void>;
    end?(end: DocumentEnd): void | Promise<void>;
}
interface Doctype {
    readonly name: string | null;
    readonly publicId: string | null;
    readonly systemId: string | null;
}
interface Element {
    tagName: string;
    readonly attributes: IterableIterator<string[]>;
    readonly removed: boolean;
    readonly namespaceURI: string;
    getAttribute(name: string): string | null;
    hasAttribute(name: string): boolean;
    setAttribute(name: string, value: string): Element;
    removeAttribute(name: string): Element;
    before(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    after(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    prepend(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    append(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    replace(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    remove(): Element;
    removeAndKeepContent(): Element;
    setInnerContent(content: string | ReadableStream | Response, options?: ContentOptions): Element;
    onEndTag(handler: (tag: EndTag) => void | Promise<void>): void;
}
interface EndTag {
    name: string;
    before(content: string | ReadableStream | Response, options?: ContentOptions): EndTag;
    after(content: string | ReadableStream | Response, options?: ContentOptions): EndTag;
    remove(): EndTag;
}
interface Comment {
    text: string;
    readonly removed: boolean;
    before(content: string, options?: ContentOptions): Comment;
    after(content: string, options?: ContentOptions): Comment;
    replace(content: string, options?: ContentOptions): Comment;
    remove(): Comment;
}
interface Text {
    readonly text: string;
    readonly lastInTextNode: boolean;
    readonly removed: boolean;
    before(content: string | ReadableStream | Response, options?: ContentOptions): Text;
    after(content: string | ReadableStream | Response, options?: ContentOptions): Text;
    replace(content: string | ReadableStream | Response, options?: ContentOptions): Text;
    remove(): Text;
}
interface DocumentEnd {
    append(content: string, options?: ContentOptions): DocumentEnd;
}
/**
 * This is the event type for fetch events dispatched on the service worker global scope. It contains information about the fetch, including the request and how the receiver will treat the response. It provides the event.respondWith() method, which allows us to provide a response to this fetch.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/FetchEvent)
 */
declare abstract class FetchEvent extends ExtendableEvent {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FetchEvent/request) */
    readonly request: Request;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/FetchEvent/respondWith) */
    respondWith(promise: Response | Promise<Response>): void;
    passThroughOnException(): void;
}
type HeadersInit = Headers | Iterable<Iterable<string>> | Record<string, string>;
/**
 * This Fetch API interface allows you to perform various actions on HTTP request and response headers. These actions include retrieving, setting, adding to, and removing. A Headers object has an associated header list, which is initially empty and consists of zero or more name and value pairs.  You can add to this using methods like append() (see Examples.) In all methods of this interface, header names are matched by case-insensitive byte sequence.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers)
 */
declare class Headers {
    constructor(init?: HeadersInit);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/get) */
    get(name: string): string | null;
    getAll(name: string): string[];
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/getSetCookie) */
    getSetCookie(): string[];
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/has) */
    has(name: string): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/set) */
    set(name: string, value: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/append) */
    append(name: string, value: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Headers/delete) */
    delete(name: string): void;
    forEach<This = unknown>(callback: (this: This, value: string, key: string, parent: Headers) => void, thisArg?: This): void;
    /* Returns an iterator allowing to go through all key/value pairs contained in this object. */
    entries(): IterableIterator<[
        key: string,
        value: string
    ]>;
    /* Returns an iterator allowing to go through all keys of the key/value pairs contained in this object. */
    keys(): IterableIterator<string>;
    /* Returns an iterator allowing to go through all values of the key/value pairs contained in this object. */
    values(): IterableIterator<string>;
    [Symbol.iterator](): IterableIterator<[
        key: string,
        value: string
    ]>;
}
type BodyInit = ReadableStream<Uint8Array> | string | ArrayBuffer | ArrayBufferView | Blob | URLSearchParams | FormData;
declare abstract class Body {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/body) */
    get body(): ReadableStream | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/bodyUsed) */
    get bodyUsed(): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/arrayBuffer) */
    arrayBuffer(): Promise<ArrayBuffer>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/bytes) */
    bytes(): Promise<Uint8Array>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/text) */
    text(): Promise<string>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/json) */
    json<T>(): Promise<T>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/formData) */
    formData(): Promise<FormData>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/blob) */
    blob(): Promise<Blob>;
}
/**
 * This Fetch API interface represents the response to a request.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response)
 */
declare var Response: {
    prototype: Response;
    new (body?: BodyInit | null, init?: ResponseInit): Response;
    error(): Response;
    redirect(url: string, status?: number): Response;
    json(any: any, maybeInit?: (ResponseInit | Response)): Response;
};
/**
 * This Fetch API interface represents the response to a request.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response)
 */
interface Response extends Body {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/clone) */
    clone(): Response;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/status) */
    status: number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/statusText) */
    statusText: string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/headers) */
    headers: Headers;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/ok) */
    ok: boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/redirected) */
    redirected: boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/url) */
    url: string;
    webSocket: WebSocket | null;
    cf: any | undefined;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Response/type) */
    type: "default" | "error";
}
interface ResponseInit {
    status?: number;
    statusText?: string;
    headers?: HeadersInit;
    cf?: any;
    webSocket?: (WebSocket | null);
    encodeBody?: "automatic" | "manual";
}
type RequestInfo<CfHostMetadata = unknown, Cf = CfProperties<CfHostMetadata>> = Request<CfHostMetadata, Cf> | string;
/**
 * This Fetch API interface represents a resource request.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request)
 */
declare var Request: {
    prototype: Request;
    new <CfHostMetadata = unknown, Cf = CfProperties<CfHostMetadata>>(input: RequestInfo<CfProperties> | URL, init?: RequestInit<Cf>): Request<CfHostMetadata, Cf>;
};
/**
 * This Fetch API interface represents a resource request.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request)
 */
interface Request<CfHostMetadata = unknown, Cf = CfProperties<CfHostMetadata>> extends Body {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/clone) */
    clone(): Request<CfHostMetadata, Cf>;
    /**
     * Returns request's HTTP method, which is "GET" by default.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/method)
     */
    method: string;
    /**
     * Returns the URL of request as a string.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/url)
     */
    url: string;
    /**
     * Returns a Headers object consisting of the headers associated with request. Note that headers added in the network layer by the user agent will not be accounted for in this object, e.g., the "Host" header.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/headers)
     */
    headers: Headers;
    /**
     * Returns the redirect mode associated with request, which is a string indicating how redirects for the request will be handled during fetching. A request will follow redirects by default.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/redirect)
     */
    redirect: string;
    fetcher: Fetcher | null;
    /**
     * Returns the signal associated with request, which is an AbortSignal object indicating whether or not request has been aborted, and its abort event handler.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/signal)
     */
    signal: AbortSignal;
    cf: Cf | undefined;
    /**
     * Returns request's subresource integrity metadata, which is a cryptographic hash of the resource being fetched. Its value consists of multiple hashes separated by whitespace. [SRI]
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/integrity)
     */
    integrity: string;
    /**
     * Returns a boolean indicating whether or not request can outlive the global in which it was created.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/keepalive)
     */
    keepalive: boolean;
    /**
     * Returns the cache mode associated with request, which is a string indicating how the request will interact with the browser's cache when fetching.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/Request/cache)
     */
    cache?: "no-store";
}
interface RequestInit<Cf = CfProperties> {
    /* A string to set request's method. */
    method?: string;
    /* A Headers object, an object literal, or an array of two-item arrays to set request's headers. */
    headers?: HeadersInit;
    /* A BodyInit object or null to set request's body. */
    body?: BodyInit | null;
    /* A string indicating whether request follows redirects, results in an error upon encountering a redirect, or returns the redirect (in an opaque fashion). Sets request's redirect. */
    redirect?: string;
    fetcher?: (Fetcher | null);
    cf?: Cf;
    /* A string indicating how the request will interact with the browser's cache to set request's cache. */
    cache?: "no-store";
    /* A cryptographic hash of the resource to be fetched by request. Sets request's integrity. */
    integrity?: string;
    /* An AbortSignal to set request's signal. */
    signal?: (AbortSignal | null);
    encodeResponseBody?: "automatic" | "manual";
}
type Service<T extends Rpc.WorkerEntrypointBranded | undefined = undefined> = Fetcher<T>;
type Fetcher<T extends Rpc.EntrypointBranded | undefined = undefined, Reserved extends string = never> = (T extends Rpc.EntrypointBranded ? Rpc.Provider<T, Reserved | "fetch" | "connect"> : unknown) & {
    fetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response>;
    connect(address: SocketAddress | string, options?: SocketOptions): Socket;
};
interface KVNamespaceListKey<Metadata, Key extends string = string> {
    name: Key;
    expiration?: number;
    metadata?: Metadata;
}
type KVNamespaceListResult<Metadata, Key extends string = string> = {
    list_complete: false;
    keys: KVNamespaceListKey<Metadata, Key>[];
    cursor: string;
    cacheStatus: string | null;
} | {
    list_complete: true;
    keys: KVNamespaceListKey<Metadata, Key>[];
    cacheStatus: string | null;
};
interface KVNamespace<Key extends string = string> {
    get(key: Key, options?: Partial<KVNamespaceGetOptions<undefined>>): Promise<string | null>;
    get(key: Key, type: "text"): Promise<string | null>;
    get<ExpectedValue = unknown>(key: Key, type: "json"): Promise<ExpectedValue | null>;
    get(key: Key, type: "arrayBuffer"): Promise<ArrayBuffer | null>;
    get(key: Key, type: "stream"): Promise<ReadableStream | null>;
    get(key: Key, options?: KVNamespaceGetOptions<"text">): Promise<string | null>;
    get<ExpectedValue = unknown>(key: Key, options?: KVNamespaceGetOptions<"json">): Promise<ExpectedValue | null>;
    get(key: Key, options?: KVNamespaceGetOptions<"arrayBuffer">): Promise<ArrayBuffer | null>;
    get(key: Key, options?: KVNamespaceGetOptions<"stream">): Promise<ReadableStream | null>;
    get(key: Array<Key>, type: "text"): Promise<Map<string, string | null>>;
    get<ExpectedValue = unknown>(key: Array<Key>, type: "json"): Promise<Map<string, ExpectedValue | null>>;
    get(key: Array<Key>, options?: Partial<KVNamespaceGetOptions<undefined>>): Promise<Map<string, string | null>>;
    get(key: Array<Key>, options?: KVNamespaceGetOptions<"text">): Promise<Map<string, string | null>>;
    get<ExpectedValue = unknown>(key: Array<Key>, options?: KVNamespaceGetOptions<"json">): Promise<Map<string, ExpectedValue | null>>;
    list<Metadata = unknown>(options?: KVNamespaceListOptions): Promise<KVNamespaceListResult<Metadata, Key>>;
    put(key: Key, value: string | ArrayBuffer | ArrayBufferView | ReadableStream, options?: KVNamespacePutOptions): Promise<void>;
    getWithMetadata<Metadata = unknown>(key: Key, options?: Partial<KVNamespaceGetOptions<undefined>>): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, type: "text"): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
    getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(key: Key, type: "json"): Promise<KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, type: "arrayBuffer"): Promise<KVNamespaceGetWithMetadataResult<ArrayBuffer, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, type: "stream"): Promise<KVNamespaceGetWithMetadataResult<ReadableStream, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, options: KVNamespaceGetOptions<"text">): Promise<KVNamespaceGetWithMetadataResult<string, Metadata>>;
    getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(key: Key, options: KVNamespaceGetOptions<"json">): Promise<KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, options: KVNamespaceGetOptions<"arrayBuffer">): Promise<KVNamespaceGetWithMetadataResult<ArrayBuffer, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Key, options: KVNamespaceGetOptions<"stream">): Promise<KVNamespaceGetWithMetadataResult<ReadableStream, Metadata>>;
    getWithMetadata<Metadata = unknown>(key: Array<Key>, type: "text"): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
    getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(key: Array<Key>, type: "json"): Promise<Map<string, KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>>;
    getWithMetadata<Metadata = unknown>(key: Array<Key>, options?: Partial<KVNamespaceGetOptions<undefined>>): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
    getWithMetadata<Metadata = unknown>(key: Array<Key>, options?: KVNamespaceGetOptions<"text">): Promise<Map<string, KVNamespaceGetWithMetadataResult<string, Metadata>>>;
    getWithMetadata<ExpectedValue = unknown, Metadata = unknown>(key: Array<Key>, options?: KVNamespaceGetOptions<"json">): Promise<Map<string, KVNamespaceGetWithMetadataResult<ExpectedValue, Metadata>>>;
    delete(key: Key): Promise<void>;
}
interface KVNamespaceListOptions {
    limit?: number;
    prefix?: (string | null);
    cursor?: (string | null);
}
interface KVNamespaceGetOptions<Type> {
    type: Type;
    cacheTtl?: number;
}
interface KVNamespacePutOptions {
    expiration?: number;
    expirationTtl?: number;
    metadata?: (any | null);
}
interface KVNamespaceGetWithMetadataResult<Value, Metadata> {
    value: Value | null;
    metadata: Metadata | null;
    cacheStatus: string | null;
}
type QueueContentType = "text" | "bytes" | "json" | "v8";
interface Queue<Body = unknown> {
    send(message: Body, options?: QueueSendOptions): Promise<void>;
    sendBatch(messages: Iterable<MessageSendRequest<Body>>, options?: QueueSendBatchOptions): Promise<void>;
}
interface QueueSendOptions {
    contentType?: QueueContentType;
    delaySeconds?: number;
}
interface QueueSendBatchOptions {
    delaySeconds?: number;
}
interface MessageSendRequest<Body = unknown> {
    body: Body;
    contentType?: QueueContentType;
    delaySeconds?: number;
}
interface QueueRetryOptions {
    delaySeconds?: number;
}
interface Message<Body = unknown> {
    readonly id: string;
    readonly timestamp: Date;
    readonly body: Body;
    readonly attempts: number;
    retry(options?: QueueRetryOptions): void;
    ack(): void;
}
interface QueueEvent<Body = unknown> extends ExtendableEvent {
    readonly messages: readonly Message<Body>[];
    readonly queue: string;
    retryAll(options?: QueueRetryOptions): void;
    ackAll(): void;
}
interface MessageBatch<Body = unknown> {
    readonly messages: readonly Message<Body>[];
    readonly queue: string;
    retryAll(options?: QueueRetryOptions): void;
    ackAll(): void;
}
interface R2Error extends Error {
    readonly name: string;
    readonly code: number;
    readonly message: string;
    readonly action: string;
    readonly stack: any;
}
interface R2ListOptions {
    limit?: number;
    prefix?: string;
    cursor?: string;
    delimiter?: string;
    startAfter?: string;
    include?: ("httpMetadata" | "customMetadata")[];
}
declare abstract class R2Bucket {
    head(key: string): Promise<R2Object | null>;
    get(key: string, options: R2GetOptions & {
        onlyIf: R2Conditional | Headers;
    }): Promise<R2ObjectBody | R2Object | null>;
    get(key: string, options?: R2GetOptions): Promise<R2ObjectBody | null>;
    put(key: string, value: ReadableStream | ArrayBuffer | ArrayBufferView | string | null | Blob, options?: R2PutOptions & {
        onlyIf: R2Conditional | Headers;
    }): Promise<R2Object | null>;
    put(key: string, value: ReadableStream | ArrayBuffer | ArrayBufferView | string | null | Blob, options?: R2PutOptions): Promise<R2Object>;
    createMultipartUpload(key: string, options?: R2MultipartOptions): Promise<R2MultipartUpload>;
    resumeMultipartUpload(key: string, uploadId: string): R2MultipartUpload;
    delete(keys: string | string[]): Promise<void>;
    list(options?: R2ListOptions): Promise<R2Objects>;
}
interface R2MultipartUpload {
    readonly key: string;
    readonly uploadId: string;
    uploadPart(partNumber: number, value: ReadableStream | (ArrayBuffer | ArrayBufferView) | string | Blob, options?: R2UploadPartOptions): Promise<R2UploadedPart>;
    abort(): Promise<void>;
    complete(uploadedParts: R2UploadedPart[]): Promise<R2Object>;
}
interface R2UploadedPart {
    partNumber: number;
    etag: string;
}
declare abstract class R2Object {
    readonly key: string;
    readonly version: string;
    readonly size: number;
    readonly etag: string;
    readonly httpEtag: string;
    readonly checksums: R2Checksums;
    readonly uploaded: Date;
    readonly httpMetadata?: R2HTTPMetadata;
    readonly customMetadata?: Record<string, string>;
    readonly range?: R2Range;
    readonly storageClass: string;
    readonly ssecKeyMd5?: string;
    writeHttpMetadata(headers: Headers): void;
}
interface R2ObjectBody extends R2Object {
    get body(): ReadableStream;
    get bodyUsed(): boolean;
    arrayBuffer(): Promise<ArrayBuffer>;
    bytes(): Promise<Uint8Array>;
    text(): Promise<string>;
    json<T>(): Promise<T>;
    blob(): Promise<Blob>;
}
type R2Range = {
    offset: number;
    length?: number;
} | {
    offset?: number;
    length: number;
} | {
    suffix: number;
};
interface R2Conditional {
    etagMatches?: string;
    etagDoesNotMatch?: string;
    uploadedBefore?: Date;
    uploadedAfter?: Date;
    secondsGranularity?: boolean;
}
interface R2GetOptions {
    onlyIf?: (R2Conditional | Headers);
    range?: (R2Range | Headers);
    ssecKey?: (ArrayBuffer | string);
}
interface R2PutOptions {
    onlyIf?: (R2Conditional | Headers);
    httpMetadata?: (R2HTTPMetadata | Headers);
    customMetadata?: Record<string, string>;
    md5?: ((ArrayBuffer | ArrayBufferView) | string);
    sha1?: ((ArrayBuffer | ArrayBufferView) | string);
    sha256?: ((ArrayBuffer | ArrayBufferView) | string);
    sha384?: ((ArrayBuffer | ArrayBufferView) | string);
    sha512?: ((ArrayBuffer | ArrayBufferView) | string);
    storageClass?: string;
    ssecKey?: (ArrayBuffer | string);
}
interface R2MultipartOptions {
    httpMetadata?: (R2HTTPMetadata | Headers);
    customMetadata?: Record<string, string>;
    storageClass?: string;
    ssecKey?: (ArrayBuffer | string);
}
interface R2Checksums {
    readonly md5?: ArrayBuffer;
    readonly sha1?: ArrayBuffer;
    readonly sha256?: ArrayBuffer;
    readonly sha384?: ArrayBuffer;
    readonly sha512?: ArrayBuffer;
    toJSON(): R2StringChecksums;
}
interface R2StringChecksums {
    md5?: string;
    sha1?: string;
    sha256?: string;
    sha384?: string;
    sha512?: string;
}
interface R2HTTPMetadata {
    contentType?: string;
    contentLanguage?: string;
    contentDisposition?: string;
    contentEncoding?: string;
    cacheControl?: string;
    cacheExpiry?: Date;
}
type R2Objects = {
    objects: R2Object[];
    delimitedPrefixes: string[];
} & ({
    truncated: true;
    cursor: string;
} | {
    truncated: false;
});
interface R2UploadPartOptions {
    ssecKey?: (ArrayBuffer | string);
}
declare abstract class ScheduledEvent extends ExtendableEvent {
    readonly scheduledTime: number;
    readonly cron: string;
    noRetry(): void;
}
interface ScheduledController {
    readonly scheduledTime: number;
    readonly cron: string;
    noRetry(): void;
}
interface QueuingStrategy<T = any> {
    highWaterMark?: (number | bigint);
    size?: (chunk: T) => number | bigint;
}
interface UnderlyingSink<W = any> {
    type?: string;
    start?: (controller: WritableStreamDefaultController) => void | Promise<void>;
    write?: (chunk: W, controller: WritableStreamDefaultController) => void | Promise<void>;
    abort?: (reason: any) => void | Promise<void>;
    close?: () => void | Promise<void>;
}
interface UnderlyingByteSource {
    type: "bytes";
    autoAllocateChunkSize?: number;
    start?: (controller: ReadableByteStreamController) => void | Promise<void>;
    pull?: (controller: ReadableByteStreamController) => void | Promise<void>;
    cancel?: (reason: any) => void | Promise<void>;
}
interface UnderlyingSource<R = any> {
    type?: "" | undefined;
    start?: (controller: ReadableStreamDefaultController<R>) => void | Promise<void>;
    pull?: (controller: ReadableStreamDefaultController<R>) => void | Promise<void>;
    cancel?: (reason: any) => void | Promise<void>;
    expectedLength?: (number | bigint);
}
interface Transformer<I = any, O = any> {
    readableType?: string;
    writableType?: string;
    start?: (controller: TransformStreamDefaultController<O>) => void | Promise<void>;
    transform?: (chunk: I, controller: TransformStreamDefaultController<O>) => void | Promise<void>;
    flush?: (controller: TransformStreamDefaultController<O>) => void | Promise<void>;
    cancel?: (reason: any) => void | Promise<void>;
    expectedLength?: number;
}
interface StreamPipeOptions {
    /**
     * Pipes this readable stream to a given writable stream destination. The way in which the piping process behaves under various error conditions can be customized with a number of passed options. It returns a promise that fulfills when the piping process completes successfully, or rejects if any errors were encountered.
     *
     * Piping a stream will lock it for the duration of the pipe, preventing any other consumer from acquiring a reader.
     *
     * Errors and closures of the source and destination streams propagate as follows:
     *
     * An error in this source readable stream will abort destination, unless preventAbort is truthy. The returned promise will be rejected with the source's error, or with any error that occurs during aborting the destination.
     *
     * An error in destination will cancel this source readable stream, unless preventCancel is truthy. The returned promise will be rejected with the destination's error, or with any error that occurs during canceling the source.
     *
     * When this source readable stream closes, destination will be closed, unless preventClose is truthy. The returned promise will be fulfilled once this process completes, unless an error is encountered while closing the destination, in which case it will be rejected with that error.
     *
     * If destination starts out closed or closing, this source readable stream will be canceled, unless preventCancel is true. The returned promise will be rejected with an error indicating piping to a closed stream failed, or with any error that occurs during canceling the source.
     *
     * The signal option can be set to an AbortSignal to allow aborting an ongoing pipe operation via the corresponding AbortController. In this case, this source readable stream will be canceled, and destination aborted, unless the respective options preventCancel or preventAbort are set.
     */
    preventClose?: boolean;
    preventAbort?: boolean;
    preventCancel?: boolean;
    signal?: AbortSignal;
}
type ReadableStreamReadResult<R = any> = {
    done: false;
    value: R;
} | {
    done: true;
    value?: undefined;
};
/**
 * This Streams API interface represents a readable stream of byte data. The Fetch API offers a concrete instance of a ReadableStream through the body property of a Response object.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream)
 */
interface ReadableStream<R = any> {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/locked) */
    get locked(): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/cancel) */
    cancel(reason?: any): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/getReader) */
    getReader(): ReadableStreamDefaultReader<R>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/getReader) */
    getReader(options: ReadableStreamGetReaderOptions): ReadableStreamBYOBReader;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/pipeThrough) */
    pipeThrough<T>(transform: ReadableWritablePair<T, R>, options?: StreamPipeOptions): ReadableStream<T>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/pipeTo) */
    pipeTo(destination: WritableStream<R>, options?: StreamPipeOptions): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream/tee) */
    tee(): [
        ReadableStream<R>,
        ReadableStream<R>
    ];
    values(options?: ReadableStreamValuesOptions): AsyncIterableIterator<R>;
    [Symbol.asyncIterator](options?: ReadableStreamValuesOptions): AsyncIterableIterator<R>;
}
/**
 * This Streams API interface represents a readable stream of byte data. The Fetch API offers a concrete instance of a ReadableStream through the body property of a Response object.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStream)
 */
declare const ReadableStream: {
    prototype: ReadableStream;
    new (underlyingSource: UnderlyingByteSource, strategy?: QueuingStrategy<Uint8Array>): ReadableStream<Uint8Array>;
    new <R = any>(underlyingSource?: UnderlyingSource<R>, strategy?: QueuingStrategy<R>): ReadableStream<R>;
};
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultReader) */
declare class ReadableStreamDefaultReader<R = any> {
    constructor(stream: ReadableStream);
    get closed(): Promise<void>;
    cancel(reason?: any): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultReader/read) */
    read(): Promise<ReadableStreamReadResult<R>>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultReader/releaseLock) */
    releaseLock(): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBReader) */
declare class ReadableStreamBYOBReader {
    constructor(stream: ReadableStream);
    get closed(): Promise<void>;
    cancel(reason?: any): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBReader/read) */
    read<T extends ArrayBufferView>(view: T): Promise<ReadableStreamReadResult<T>>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBReader/releaseLock) */
    releaseLock(): void;
    readAtLeast<T extends ArrayBufferView>(minElements: number, view: T): Promise<ReadableStreamReadResult<T>>;
}
interface ReadableStreamBYOBReaderReadableStreamBYOBReaderReadOptions {
    min?: number;
}
interface ReadableStreamGetReaderOptions {
    /**
     * Creates a ReadableStreamBYOBReader and locks the stream to the new reader.
     *
     * This call behaves the same way as the no-argument variant, except that it only works on readable byte streams, i.e. streams which were constructed specifically with the ability to handle "bring your own buffer" reading. The returned BYOB reader provides the ability to directly read individual chunks from the stream via its read() method, into developer-supplied buffers, allowing more precise control over allocation.
     */
    mode: "byob";
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBRequest) */
declare abstract class ReadableStreamBYOBRequest {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBRequest/view) */
    get view(): Uint8Array | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBRequest/respond) */
    respond(bytesWritten: number): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamBYOBRequest/respondWithNewView) */
    respondWithNewView(view: ArrayBuffer | ArrayBufferView): void;
    get atLeast(): number | null;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultController) */
declare abstract class ReadableStreamDefaultController<R = any> {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultController/desiredSize) */
    get desiredSize(): number | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultController/close) */
    close(): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultController/enqueue) */
    enqueue(chunk?: R): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableStreamDefaultController/error) */
    error(reason: any): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController) */
declare abstract class ReadableByteStreamController {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController/byobRequest) */
    get byobRequest(): ReadableStreamBYOBRequest | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController/desiredSize) */
    get desiredSize(): number | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController/close) */
    close(): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController/enqueue) */
    enqueue(chunk: ArrayBuffer | ArrayBufferView): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ReadableByteStreamController/error) */
    error(reason: any): void;
}
/**
 * This Streams API interface represents a controller allowing control of a WritableStream's state. When constructing a WritableStream, the underlying sink is given a corresponding WritableStreamDefaultController instance to manipulate.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultController)
 */
declare abstract class WritableStreamDefaultController {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultController/signal) */
    get signal(): AbortSignal;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultController/error) */
    error(reason?: any): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStreamDefaultController) */
declare abstract class TransformStreamDefaultController<O = any> {
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStreamDefaultController/desiredSize) */
    get desiredSize(): number | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStreamDefaultController/enqueue) */
    enqueue(chunk?: O): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStreamDefaultController/error) */
    error(reason: any): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStreamDefaultController/terminate) */
    terminate(): void;
}
interface ReadableWritablePair<R = any, W = any> {
    /**
     * Provides a convenient, chainable way of piping this readable stream through a transform stream (or any other { writable, readable } pair). It simply pipes the stream into the writable side of the supplied pair, and returns the readable side for further use.
     *
     * Piping a stream will lock it for the duration of the pipe, preventing any other consumer from acquiring a reader.
     */
    writable: WritableStream<W>;
    readable: ReadableStream<R>;
}
/**
 * This Streams API interface provides a standard abstraction for writing streaming data to a destination, known as a sink. This object comes with built-in backpressure and queuing.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStream)
 */
declare class WritableStream<W = any> {
    constructor(underlyingSink?: UnderlyingSink, queuingStrategy?: QueuingStrategy);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStream/locked) */
    get locked(): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStream/abort) */
    abort(reason?: any): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStream/close) */
    close(): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStream/getWriter) */
    getWriter(): WritableStreamDefaultWriter<W>;
}
/**
 * This Streams API interface is the object returned by WritableStream.getWriter() and once created locks the < writer to the WritableStream ensuring that no other streams can write to the underlying sink.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter)
 */
declare class WritableStreamDefaultWriter<W = any> {
    constructor(stream: WritableStream);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/closed) */
    get closed(): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/ready) */
    get ready(): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/desiredSize) */
    get desiredSize(): number | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/abort) */
    abort(reason?: any): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/close) */
    close(): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/write) */
    write(chunk?: W): Promise<void>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/WritableStreamDefaultWriter/releaseLock) */
    releaseLock(): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStream) */
declare class TransformStream<I = any, O = any> {
    constructor(transformer?: Transformer<I, O>, writableStrategy?: QueuingStrategy<I>, readableStrategy?: QueuingStrategy<O>);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStream/readable) */
    get readable(): ReadableStream<O>;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TransformStream/writable) */
    get writable(): WritableStream<I>;
}
declare class FixedLengthStream extends IdentityTransformStream {
    constructor(expectedLength: number | bigint, queuingStrategy?: IdentityTransformStreamQueuingStrategy);
}
declare class IdentityTransformStream extends TransformStream<ArrayBuffer | ArrayBufferView, Uint8Array> {
    constructor(queuingStrategy?: IdentityTransformStreamQueuingStrategy);
}
interface IdentityTransformStreamQueuingStrategy {
    highWaterMark?: (number | bigint);
}
interface ReadableStreamValuesOptions {
    preventCancel?: boolean;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CompressionStream) */
declare class CompressionStream extends TransformStream<ArrayBuffer | ArrayBufferView, Uint8Array> {
    constructor(format: "gzip" | "deflate" | "deflate-raw");
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/DecompressionStream) */
declare class DecompressionStream extends TransformStream<ArrayBuffer | ArrayBufferView, Uint8Array> {
    constructor(format: "gzip" | "deflate" | "deflate-raw");
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextEncoderStream) */
declare class TextEncoderStream extends TransformStream<string, Uint8Array> {
    constructor();
    get encoding(): string;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/TextDecoderStream) */
declare class TextDecoderStream extends TransformStream<ArrayBuffer | ArrayBufferView, string> {
    constructor(label?: string, options?: TextDecoderStreamTextDecoderStreamInit);
    get encoding(): string;
    get fatal(): boolean;
    get ignoreBOM(): boolean;
}
interface TextDecoderStreamTextDecoderStreamInit {
    fatal?: boolean;
    ignoreBOM?: boolean;
}
/**
 * This Streams API interface provides a built-in byte length queuing strategy that can be used when constructing streams.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/ByteLengthQueuingStrategy)
 */
declare class ByteLengthQueuingStrategy implements QueuingStrategy<ArrayBufferView> {
    constructor(init: QueuingStrategyInit);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ByteLengthQueuingStrategy/highWaterMark) */
    get highWaterMark(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/ByteLengthQueuingStrategy/size) */
    get size(): (chunk?: any) => number;
}
/**
 * This Streams API interface provides a built-in byte length queuing strategy that can be used when constructing streams.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CountQueuingStrategy)
 */
declare class CountQueuingStrategy implements QueuingStrategy {
    constructor(init: QueuingStrategyInit);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CountQueuingStrategy/highWaterMark) */
    get highWaterMark(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/CountQueuingStrategy/size) */
    get size(): (chunk?: any) => number;
}
interface QueuingStrategyInit {
    /**
     * Creates a new ByteLengthQueuingStrategy with the provided high water mark.
     *
     * Note that the provided high water mark will not be validated ahead of time. Instead, if it is negative, NaN, or not a number, the resulting ByteLengthQueuingStrategy will cause the corresponding stream constructor to throw.
     */
    highWaterMark: number;
}
interface ScriptVersion {
    id?: string;
    tag?: string;
    message?: string;
}
declare abstract class TailEvent extends ExtendableEvent {
    readonly events: TraceItem[];
    readonly traces: TraceItem[];
}
interface TraceItem {
    readonly event: (TraceItemFetchEventInfo | TraceItemJsRpcEventInfo | TraceItemScheduledEventInfo | TraceItemAlarmEventInfo | TraceItemQueueEventInfo | TraceItemEmailEventInfo | TraceItemTailEventInfo | TraceItemCustomEventInfo | TraceItemHibernatableWebSocketEventInfo) | null;
    readonly eventTimestamp: number | null;
    readonly logs: TraceLog[];
    readonly exceptions: TraceException[];
    readonly diagnosticsChannelEvents: TraceDiagnosticChannelEvent[];
    readonly scriptName: string | null;
    readonly entrypoint?: string;
    readonly scriptVersion?: ScriptVersion;
    readonly dispatchNamespace?: string;
    readonly scriptTags?: string[];
    readonly outcome: string;
    readonly executionModel: string;
    readonly truncated: boolean;
    readonly cpuTime: number;
    readonly wallTime: number;
}
interface TraceItemAlarmEventInfo {
    readonly scheduledTime: Date;
}
interface TraceItemCustomEventInfo {
}
interface TraceItemScheduledEventInfo {
    readonly scheduledTime: number;
    readonly cron: string;
}
interface TraceItemQueueEventInfo {
    readonly queue: string;
    readonly batchSize: number;
}
interface TraceItemEmailEventInfo {
    readonly mailFrom: string;
    readonly rcptTo: string;
    readonly rawSize: number;
}
interface TraceItemTailEventInfo {
    readonly consumedEvents: TraceItemTailEventInfoTailItem[];
}
interface TraceItemTailEventInfoTailItem {
    readonly scriptName: string | null;
}
interface TraceItemFetchEventInfo {
    readonly response?: TraceItemFetchEventInfoResponse;
    readonly request: TraceItemFetchEventInfoRequest;
}
interface TraceItemFetchEventInfoRequest {
    readonly cf?: any;
    readonly headers: Record<string, string>;
    readonly method: string;
    readonly url: string;
    getUnredacted(): TraceItemFetchEventInfoRequest;
}
interface TraceItemFetchEventInfoResponse {
    readonly status: number;
}
interface TraceItemJsRpcEventInfo {
    readonly rpcMethod: string;
}
interface TraceItemHibernatableWebSocketEventInfo {
    readonly getWebSocketEvent: TraceItemHibernatableWebSocketEventInfoMessage | TraceItemHibernatableWebSocketEventInfoClose | TraceItemHibernatableWebSocketEventInfoError;
}
interface TraceItemHibernatableWebSocketEventInfoMessage {
    readonly webSocketEventType: string;
}
interface TraceItemHibernatableWebSocketEventInfoClose {
    readonly webSocketEventType: string;
    readonly code: number;
    readonly wasClean: boolean;
}
interface TraceItemHibernatableWebSocketEventInfoError {
    readonly webSocketEventType: string;
}
interface TraceLog {
    readonly timestamp: number;
    readonly level: string;
    readonly message: any;
}
interface TraceException {
    readonly timestamp: number;
    readonly message: string;
    readonly name: string;
    readonly stack?: string;
}
interface TraceDiagnosticChannelEvent {
    readonly timestamp: number;
    readonly channel: string;
    readonly message: any;
}
interface TraceMetrics {
    readonly cpuTime: number;
    readonly wallTime: number;
}
interface UnsafeTraceMetrics {
    fromTrace(item: TraceItem): TraceMetrics;
}
/**
 * The URL interface represents an object providing static methods used for creating object URLs.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL)
 */
declare class URL {
    constructor(url: string | URL, base?: string | URL);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/origin) */
    get origin(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/href) */
    get href(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/href) */
    set href(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/protocol) */
    get protocol(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/protocol) */
    set protocol(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/username) */
    get username(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/username) */
    set username(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/password) */
    get password(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/password) */
    set password(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/host) */
    get host(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/host) */
    set host(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/hostname) */
    get hostname(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/hostname) */
    set hostname(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/port) */
    get port(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/port) */
    set port(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/pathname) */
    get pathname(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/pathname) */
    set pathname(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/search) */
    get search(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/search) */
    set search(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/hash) */
    get hash(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/hash) */
    set hash(value: string);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/searchParams) */
    get searchParams(): URLSearchParams;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/toJSON) */
    toJSON(): string;
    /*function toString() { [native code] }*/
    toString(): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/canParse_static) */
    static canParse(url: string, base?: string): boolean;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/parse_static) */
    static parse(url: string, base?: string): URL | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/createObjectURL_static) */
    static createObjectURL(object: File | Blob): string;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URL/revokeObjectURL_static) */
    static revokeObjectURL(object_url: string): void;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams) */
declare class URLSearchParams {
    constructor(init?: (Iterable<Iterable<string>> | Record<string, string> | string));
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/size) */
    get size(): number;
    /**
     * Appends a specified key/value pair as a new search parameter.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/append)
     */
    append(name: string, value: string): void;
    /**
     * Deletes the given search parameter, and its associated value, from the list of all search parameters.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/delete)
     */
    delete(name: string, value?: string): void;
    /**
     * Returns the first value associated to the given search parameter.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/get)
     */
    get(name: string): string | null;
    /**
     * Returns all the values association with a given search parameter.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/getAll)
     */
    getAll(name: string): string[];
    /**
     * Returns a Boolean indicating if such a search parameter exists.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/has)
     */
    has(name: string, value?: string): boolean;
    /**
     * Sets the value associated to a given search parameter to the given value. If there were several values, delete the others.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/set)
     */
    set(name: string, value: string): void;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/URLSearchParams/sort) */
    sort(): void;
    /* Returns an array of key, value pairs for every entry in the search params. */
    entries(): IterableIterator<[
        key: string,
        value: string
    ]>;
    /* Returns a list of keys in the search params. */
    keys(): IterableIterator<string>;
    /* Returns a list of values in the search params. */
    values(): IterableIterator<string>;
    forEach<This = unknown>(callback: (this: This, value: string, key: string, parent: URLSearchParams) => void, thisArg?: This): void;
    /*function toString() { [native code] } Returns a string containing a query string suitable for use in a URL. Does not include the question mark. */
    toString(): string;
    [Symbol.iterator](): IterableIterator<[
        key: string,
        value: string
    ]>;
}
declare class URLPattern {
    constructor(input?: (string | URLPatternInit), baseURL?: (string | URLPatternOptions), patternOptions?: URLPatternOptions);
    get protocol(): string;
    get username(): string;
    get password(): string;
    get hostname(): string;
    get port(): string;
    get pathname(): string;
    get search(): string;
    get hash(): string;
    test(input?: (string | URLPatternInit), baseURL?: string): boolean;
    exec(input?: (string | URLPatternInit), baseURL?: string): URLPatternResult | null;
}
interface URLPatternInit {
    protocol?: string;
    username?: string;
    password?: string;
    hostname?: string;
    port?: string;
    pathname?: string;
    search?: string;
    hash?: string;
    baseURL?: string;
}
interface URLPatternComponentResult {
    input: string;
    groups: Record<string, string>;
}
interface URLPatternResult {
    inputs: (string | URLPatternInit)[];
    protocol: URLPatternComponentResult;
    username: URLPatternComponentResult;
    password: URLPatternComponentResult;
    hostname: URLPatternComponentResult;
    port: URLPatternComponentResult;
    pathname: URLPatternComponentResult;
    search: URLPatternComponentResult;
    hash: URLPatternComponentResult;
}
interface URLPatternOptions {
    ignoreCase?: boolean;
}
/**
 * A CloseEvent is sent to clients using WebSockets when the connection is closed. This is delivered to the listener indicated by the WebSocket object's onclose attribute.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CloseEvent)
 */
declare class CloseEvent extends Event {
    constructor(type: string, initializer?: CloseEventInit);
    /**
     * Returns the WebSocket connection close code provided by the server.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CloseEvent/code)
     */
    readonly code: number;
    /**
     * Returns the WebSocket connection close reason provided by the server.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CloseEvent/reason)
     */
    readonly reason: string;
    /**
     * Returns true if the connection closed cleanly; false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/CloseEvent/wasClean)
     */
    readonly wasClean: boolean;
}
interface CloseEventInit {
    code?: number;
    reason?: string;
    wasClean?: boolean;
}
/**
 * A message received by a target object.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/MessageEvent)
 */
declare class MessageEvent extends Event {
    constructor(type: string, initializer: MessageEventInit);
    /**
     * Returns the data of the message.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/MessageEvent/data)
     */
    readonly data: ArrayBuffer | string;
}
interface MessageEventInit {
    data: ArrayBuffer | string;
}
type WebSocketEventMap = {
    close: CloseEvent;
    message: MessageEvent;
    open: Event;
    error: ErrorEvent;
};
/**
 * Provides the API for creating and managing a WebSocket connection to a server, as well as for sending and receiving data on the connection.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket)
 */
declare var WebSocket: {
    prototype: WebSocket;
    new (url: string, protocols?: (string[] | string)): WebSocket;
    readonly READY_STATE_CONNECTING: number;
    readonly CONNECTING: number;
    readonly READY_STATE_OPEN: number;
    readonly OPEN: number;
    readonly READY_STATE_CLOSING: number;
    readonly CLOSING: number;
    readonly READY_STATE_CLOSED: number;
    readonly CLOSED: number;
};
/**
 * Provides the API for creating and managing a WebSocket connection to a server, as well as for sending and receiving data on the connection.
 *
 * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket)
 */
interface WebSocket extends EventTarget<WebSocketEventMap> {
    accept(): void;
    /**
     * Transmits data using the WebSocket connection. data can be a string, a Blob, an ArrayBuffer, or an ArrayBufferView.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/send)
     */
    send(message: (ArrayBuffer | ArrayBufferView) | string): void;
    /**
     * Closes the WebSocket connection, optionally using code as the the WebSocket connection close code and reason as the the WebSocket connection close reason.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/close)
     */
    close(code?: number, reason?: string): void;
    serializeAttachment(attachment: any): void;
    deserializeAttachment(): any | null;
    /**
     * Returns the state of the WebSocket object's connection. It can have the values described below.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/readyState)
     */
    readyState: number;
    /**
     * Returns the URL that was used to establish the WebSocket connection.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/url)
     */
    url: string | null;
    /**
     * Returns the subprotocol selected by the server, if any. It can be used in conjunction with the array form of the constructor's second argument to perform subprotocol negotiation.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/protocol)
     */
    protocol: string | null;
    /**
     * Returns the extensions selected by the server, if any.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/WebSocket/extensions)
     */
    extensions: string | null;
}
declare const WebSocketPair: {
    new (): {
        0: WebSocket;
        1: WebSocket;
    };
};
interface SqlStorage {
    exec<T extends Record<string, SqlStorageValue>>(query: string, ...bindings: any[]): SqlStorageCursor<T>;
    get databaseSize(): number;
    Cursor: typeof SqlStorageCursor;
    Statement: typeof SqlStorageStatement;
}
declare abstract class SqlStorageStatement {
}
type SqlStorageValue = ArrayBuffer | string | number | null;
declare abstract class SqlStorageCursor<T extends Record<string, SqlStorageValue>> {
    next(): {
        done?: false;
        value: T;
    } | {
        done: true;
        value?: never;
    };
    toArray(): T[];
    one(): T;
    raw<U extends SqlStorageValue[]>(): IterableIterator<U>;
    columnNames: string[];
    get rowsRead(): number;
    get rowsWritten(): number;
    [Symbol.iterator](): IterableIterator<T>;
}
interface Socket {
    get readable(): ReadableStream;
    get writable(): WritableStream;
    get closed(): Promise<void>;
    get opened(): Promise<SocketInfo>;
    get upgraded(): boolean;
    get secureTransport(): "on" | "off" | "starttls";
    close(): Promise<void>;
    startTls(options?: TlsOptions): Socket;
}
interface SocketOptions {
    secureTransport?: string;
    allowHalfOpen: boolean;
    highWaterMark?: (number | bigint);
}
interface SocketAddress {
    hostname: string;
    port: number;
}
interface TlsOptions {
    expectedServerHostname?: string;
}
interface SocketInfo {
    remoteAddress?: string;
    localAddress?: string;
}
/* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource) */
declare class EventSource extends EventTarget {
    constructor(url: string, init?: EventSourceEventSourceInit);
    /**
     * Aborts any instances of the fetch algorithm started for this EventSource object, and sets the readyState attribute to CLOSED.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/close)
     */
    close(): void;
    /**
     * Returns the URL providing the event stream.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/url)
     */
    get url(): string;
    /**
     * Returns true if the credentials mode for connection requests to the URL providing the event stream is set to "include", and false otherwise.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/withCredentials)
     */
    get withCredentials(): boolean;
    /**
     * Returns the state of this EventSource object's connection. It can have the values described below.
     *
     * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/readyState)
     */
    get readyState(): number;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/open_event) */
    get onopen(): any | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/open_event) */
    set onopen(value: any | null);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/message_event) */
    get onmessage(): any | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/message_event) */
    set onmessage(value: any | null);
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/error_event) */
    get onerror(): any | null;
    /* [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/error_event) */
    set onerror(value: any | null);
    static readonly CONNECTING: number;
    static readonly OPEN: number;
    static readonly CLOSED: number;
    static from(stream: ReadableStream): EventSource;
}
interface EventSourceEventSourceInit {
    withCredentials?: boolean;
    fetcher?: Fetcher;
}
interface Container {
    get running(): boolean;
    start(options?: ContainerStartupOptions): void;
    monitor(): Promise<void>;
    destroy(error?: any): Promise<void>;
    signal(signo: number): void;
    getTcpPort(port: number): Fetcher;
}
interface ContainerStartupOptions {
    entrypoint?: string[];
    enableInternet: boolean;
    env?: Record<string, string>;
}
type AiImageClassificationInput = {
    image: number[];
};
type AiImageClassificationOutput = {
    score?: number;
    label?: string;
}[];
declare abstract class BaseAiImageClassification {
    inputs: AiImageClassificationInput;
    postProcessedOutputs: AiImageClassificationOutput;
}
type AiImageToTextInput = {
    image: number[];
    prompt?: string;
    max_tokens?: number;
    temperature?: number;
    top_p?: number;
    top_k?: number;
    seed?: number;
    repetition_penalty?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    raw?: boolean;
    messages?: RoleScopedChatInput[];
};
type AiImageToTextOutput = {
    description: string;
};
declare abstract class BaseAiImageToText {
    inputs: AiImageToTextInput;
    postProcessedOutputs: AiImageToTextOutput;
}
type AiImageTextToTextInput = {
    image: string;
    prompt?: string;
    max_tokens?: number;
    temperature?: number;
    ignore_eos?: boolean;
    top_p?: number;
    top_k?: number;
    seed?: number;
    repetition_penalty?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    raw?: boolean;
    messages?: RoleScopedChatInput[];
};
type AiImageTextToTextOutput = {
    description: string;
};
declare abstract class BaseAiImageTextToText {
    inputs: AiImageTextToTextInput;
    postProcessedOutputs: AiImageTextToTextOutput;
}
type AiObjectDetectionInput = {
    image: number[];
};
type AiObjectDetectionOutput = {
    score?: number;
    label?: string;
}[];
declare abstract class BaseAiObjectDetection {
    inputs: AiObjectDetectionInput;
    postProcessedOutputs: AiObjectDetectionOutput;
}
type AiSentenceSimilarityInput = {
    source: string;
    sentences: string[];
};
type AiSentenceSimilarityOutput = number[];
declare abstract class BaseAiSentenceSimilarity {
    inputs: AiSentenceSimilarityInput;
    postProcessedOutputs: AiSentenceSimilarityOutput;
}
type AiAutomaticSpeechRecognitionInput = {
    audio: number[];
};
type AiAutomaticSpeechRecognitionOutput = {
    text?: string;
    words?: {
        word: string;
        start: number;
        end: number;
    }[];
    vtt?: string;
};
declare abstract class BaseAiAutomaticSpeechRecognition {
    inputs: AiAutomaticSpeechRecognitionInput;
    postProcessedOutputs: AiAutomaticSpeechRecognitionOutput;
}
type AiSummarizationInput = {
    input_text: string;
    max_length?: number;
};
type AiSummarizationOutput = {
    summary: string;
};
declare abstract class BaseAiSummarization {
    inputs: AiSummarizationInput;
    postProcessedOutputs: AiSummarizationOutput;
}
type AiTextClassificationInput = {
    text: string;
};
type AiTextClassificationOutput = {
    score?: number;
    label?: string;
}[];
declare abstract class BaseAiTextClassification {
    inputs: AiTextClassificationInput;
    postProcessedOutputs: AiTextClassificationOutput;
}
type AiTextEmbeddingsInput = {
    text: string | string[];
};
type AiTextEmbeddingsOutput = {
    shape: number[];
    data: number[][];
};
declare abstract class BaseAiTextEmbeddings {
    inputs: AiTextEmbeddingsInput;
    postProcessedOutputs: AiTextEmbeddingsOutput;
}
type RoleScopedChatInput = {
    role: "user" | "assistant" | "system" | "tool" | (string & NonNullable<unknown>);
    content: string;
    name?: string;
};
type AiTextGenerationToolLegacyInput = {
    name: string;
    description: string;
    parameters?: {
        type: "object" | (string & NonNullable<unknown>);
        properties: {
            [key: string]: {
                type: string;
                description?: string;
            };
        };
        required: string[];
    };
};
type AiTextGenerationToolInput = {
    type: "function" | (string & NonNullable<unknown>);
    function: {
        name: string;
        description: string;
        parameters?: {
            type: "object" | (string & NonNullable<unknown>);
            properties: {
                [key: string]: {
                    type: string;
                    description?: string;
                };
            };
            required: string[];
        };
    };
};
type AiTextGenerationFunctionsInput = {
    name: string;
    code: string;
};
type AiTextGenerationResponseFormat = {
    type: string;
    json_schema?: any;
};
type AiTextGenerationInput = {
    prompt?: string;
    raw?: boolean;
    stream?: boolean;
    max_tokens?: number;
    temperature?: number;
    top_p?: number;
    top_k?: number;
    seed?: number;
    repetition_penalty?: number;
    frequency_penalty?: number;
    presence_penalty?: number;
    messages?: RoleScopedChatInput[];
    response_format?: AiTextGenerationResponseFormat;
    tools?: AiTextGenerationToolInput[] | AiTextGenerationToolLegacyInput[] | (object & NonNullable<unknown>);
    functions?: AiTextGenerationFunctionsInput[];
};
type AiTextGenerationOutput = {
    response?: string;
    tool_calls?: {
        name: string;
        arguments: unknown;
    }[];
};
declare abstract class BaseAiTextGeneration {
    inputs: AiTextGenerationInput;
    postProcessedOutputs: AiTextGenerationOutput;
}
type AiTextToSpeechInput = {
    prompt: string;
    lang?: string;
};
type AiTextToSpeechOutput = Uint8Array | {
    audio: string;
};
declare abstract class BaseAiTextToSpeech {
    inputs: AiTextToSpeechInput;
    postProcessedOutputs: AiTextToSpeechOutput;
}
type AiTextToImageInput = {
    prompt: string;
    negative_prompt?: string;
    height?: number;
    width?: number;
    image?: number[];
    image_b64?: string;
    mask?: number[];
    num_steps?: number;
    strength?: number;
    guidance?: number;
    seed?: number;
};
type AiTextToImageOutput = ReadableStream<Uint8Array>;
declare abstract class BaseAiTextToImage {
    inputs: AiTextToImageInput;
    postProcessedOutputs: AiTextToImageOutput;
}
type AiTranslationInput = {
    text: string;
    target_lang: string;
    source_lang?: string;
};
type AiTranslationOutput = {
    translated_text?: string;
};
declare abstract class BaseAiTranslation {
    inputs: AiTranslationInput;
    postProcessedOutputs: AiTranslationOutput;
}
type Ai_Cf_Baai_Bge_Base_En_V1_5_Input = {
    text: string | string[];
    /**
     * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
     */
    pooling?: "mean" | "cls";
} | {
    /**
     * Batch of the embeddings requests to run using async-queue
     */
    requests: {
        text: string | string[];
        /**
         * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
         */
        pooling?: "mean" | "cls";
    }[];
};
type Ai_Cf_Baai_Bge_Base_En_V1_5_Output = {
    shape?: number[];
    /**
     * Embeddings of the requested text values
     */
    data?: number[][];
    /**
     * The pooling method used in the embedding process.
     */
    pooling?: "mean" | "cls";
} | AsyncResponse;
interface AsyncResponse {
    /**
     * The async request id that can be used to obtain the results.
     */
    request_id?: string;
}
declare abstract class Base_Ai_Cf_Baai_Bge_Base_En_V1_5 {
    inputs: Ai_Cf_Baai_Bge_Base_En_V1_5_Input;
    postProcessedOutputs: Ai_Cf_Baai_Bge_Base_En_V1_5_Output;
}
type Ai_Cf_Openai_Whisper_Input = string | {
    /**
     * An array of integers that represent the audio data constrained to 8-bit unsigned integer values
     */
    audio: number[];
};
interface Ai_Cf_Openai_Whisper_Output {
    /**
     * The transcription
     */
    text: string;
    word_count?: number;
    words?: {
        word?: string;
        /**
         * The second this word begins in the recording
         */
        start?: number;
        /**
         * The ending second when the word completes
         */
        end?: number;
    }[];
    vtt?: string;
}
declare abstract class Base_Ai_Cf_Openai_Whisper {
    inputs: Ai_Cf_Openai_Whisper_Input;
    postProcessedOutputs: Ai_Cf_Openai_Whisper_Output;
}
type Ai_Cf_Meta_M2M100_1_2B_Input = {
    /**
     * The text to be translated
     */
    text: string;
    /**
     * The language code of the source text (e.g., 'en' for English). Defaults to 'en' if not specified
     */
    source_lang?: string;
    /**
     * The language code to translate the text into (e.g., 'es' for Spanish)
     */
    target_lang: string;
} | {
    /**
     * Batch of the embeddings requests to run using async-queue
     */
    requests: {
        /**
         * The text to be translated
         */
        text: string;
        /**
         * The language code of the source text (e.g., 'en' for English). Defaults to 'en' if not specified
         */
        source_lang?: string;
        /**
         * The language code to translate the text into (e.g., 'es' for Spanish)
         */
        target_lang: string;
    }[];
};
type Ai_Cf_Meta_M2M100_1_2B_Output = {
    /**
     * The translated text in the target language
     */
    translated_text?: string;
} | AsyncResponse;
declare abstract class Base_Ai_Cf_Meta_M2M100_1_2B {
    inputs: Ai_Cf_Meta_M2M100_1_2B_Input;
    postProcessedOutputs: Ai_Cf_Meta_M2M100_1_2B_Output;
}
type Ai_Cf_Baai_Bge_Small_En_V1_5_Input = {
    text: string | string[];
    /**
     * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
     */
    pooling?: "mean" | "cls";
} | {
    /**
     * Batch of the embeddings requests to run using async-queue
     */
    requests: {
        text: string | string[];
        /**
         * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
         */
        pooling?: "mean" | "cls";
    }[];
};
type Ai_Cf_Baai_Bge_Small_En_V1_5_Output = {
    shape?: number[];
    /**
     * Embeddings of the requested text values
     */
    data?: number[][];
    /**
     * The pooling method used in the embedding process.
     */
    pooling?: "mean" | "cls";
} | AsyncResponse;
declare abstract class Base_Ai_Cf_Baai_Bge_Small_En_V1_5 {
    inputs: Ai_Cf_Baai_Bge_Small_En_V1_5_Input;
    postProcessedOutputs: Ai_Cf_Baai_Bge_Small_En_V1_5_Output;
}
type Ai_Cf_Baai_Bge_Large_En_V1_5_Input = {
    text: string | string[];
    /**
     * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
     */
    pooling?: "mean" | "cls";
} | {
    /**
     * Batch of the embeddings requests to run using async-queue
     */
    requests: {
        text: string | string[];
        /**
         * The pooling method used in the embedding process. `cls` pooling will generate more accurate embeddings on larger inputs - however, embeddings created with cls pooling are not compatible with embeddings generated with mean pooling. The default pooling method is `mean` in order for this to not be a breaking change, but we highly suggest using the new `cls` pooling for better accuracy.
         */
        pooling?: "mean" | "cls";
    }[];
};
type Ai_Cf_Baai_Bge_Large_En_V1_5_Output = {
    shape?: number[];
    /**
     * Embeddings of the requested text values
     */
    data?: number[][];
    /**
     * The pooling method used in the embedding process.
     */
    pooling?: "mean" | "cls";
} | AsyncResponse;
declare abstract class Base_Ai_Cf_Baai_Bge_Large_En_V1_5 {
    inputs: Ai_Cf_Baai_Bge_Large_En_V1_5_Input;
    postProcessedOutputs: Ai_Cf_Baai_Bge_Large_En_V1_5_Output;
}
type Ai_Cf_Unum_Uform_Gen2_Qwen_500M_Input = string | {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt?: string;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * Controls the creativity of the AI's responses by adjusting how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
    image: number[] | (string & NonNullable<unknown>);
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
};
interface Ai_Cf_Unum_Uform_Gen2_Qwen_500M_Output {
    description?: string;
}
declare abstract class Base_Ai_Cf_Unum_Uform_Gen2_Qwen_500M {
    inputs: Ai_Cf_Unum_Uform_Gen2_Qwen_500M_Input;
    postProcessedOutputs: Ai_Cf_Unum_Uform_Gen2_Qwen_500M_Output;
}
type Ai_Cf_Openai_Whisper_Tiny_En_Input = string | {
    /**
     * An array of integers that represent the audio data constrained to 8-bit unsigned integer values
     */
    audio: number[];
};
interface Ai_Cf_Openai_Whisper_Tiny_En_Output {
    /**
     * The transcription
     */
    text: string;
    word_count?: number;
    words?: {
        word?: string;
        /**
         * The second this word begins in the recording
         */
        start?: number;
        /**
         * The ending second when the word completes
         */
        end?: number;
    }[];
    vtt?: string;
}
declare abstract class Base_Ai_Cf_Openai_Whisper_Tiny_En {
    inputs: Ai_Cf_Openai_Whisper_Tiny_En_Input;
    postProcessedOutputs: Ai_Cf_Openai_Whisper_Tiny_En_Output;
}
interface Ai_Cf_Openai_Whisper_Large_V3_Turbo_Input {
    /**
     * Base64 encoded value of the audio data.
     */
    audio: string;
    /**
     * Supported tasks are 'translate' or 'transcribe'.
     */
    task?: string;
    /**
     * The language of the audio being transcribed or translated.
     */
    language?: string;
    /**
     * Preprocess the audio with a voice activity detection model.
     */
    vad_filter?: boolean;
    /**
     * A text prompt to help provide context to the model on the contents of the audio.
     */
    initial_prompt?: string;
    /**
     * The prefix it appended the the beginning of the output of the transcription and can guide the transcription result.
     */
    prefix?: string;
}
interface Ai_Cf_Openai_Whisper_Large_V3_Turbo_Output {
    transcription_info?: {
        /**
         * The language of the audio being transcribed or translated.
         */
        language?: string;
        /**
         * The confidence level or probability of the detected language being accurate, represented as a decimal between 0 and 1.
         */
        language_probability?: number;
        /**
         * The total duration of the original audio file, in seconds.
         */
        duration?: number;
        /**
         * The duration of the audio after applying Voice Activity Detection (VAD) to remove silent or irrelevant sections, in seconds.
         */
        duration_after_vad?: number;
    };
    /**
     * The complete transcription of the audio.
     */
    text: string;
    /**
     * The total number of words in the transcription.
     */
    word_count?: number;
    segments?: {
        /**
         * The starting time of the segment within the audio, in seconds.
         */
        start?: number;
        /**
         * The ending time of the segment within the audio, in seconds.
         */
        end?: number;
        /**
         * The transcription of the segment.
         */
        text?: string;
        /**
         * The temperature used in the decoding process, controlling randomness in predictions. Lower values result in more deterministic outputs.
         */
        temperature?: number;
        /**
         * The average log probability of the predictions for the words in this segment, indicating overall confidence.
         */
        avg_logprob?: number;
        /**
         * The compression ratio of the input to the output, measuring how much the text was compressed during the transcription process.
         */
        compression_ratio?: number;
        /**
         * The probability that the segment contains no speech, represented as a decimal between 0 and 1.
         */
        no_speech_prob?: number;
        words?: {
            /**
             * The individual word transcribed from the audio.
             */
            word?: string;
            /**
             * The starting time of the word within the audio, in seconds.
             */
            start?: number;
            /**
             * The ending time of the word within the audio, in seconds.
             */
            end?: number;
        }[];
    }[];
    /**
     * The transcription in WebVTT format, which includes timing and text information for use in subtitles.
     */
    vtt?: string;
}
declare abstract class Base_Ai_Cf_Openai_Whisper_Large_V3_Turbo {
    inputs: Ai_Cf_Openai_Whisper_Large_V3_Turbo_Input;
    postProcessedOutputs: Ai_Cf_Openai_Whisper_Large_V3_Turbo_Output;
}
type Ai_Cf_Baai_Bge_M3_Input = BGEM3InputQueryAndContexts | BGEM3InputEmbedding | {
    /**
     * Batch of the embeddings requests to run using async-queue
     */
    requests: (BGEM3InputQueryAndContexts1 | BGEM3InputEmbedding1)[];
};
interface BGEM3InputQueryAndContexts {
    /**
     * A query you wish to perform against the provided contexts. If no query is provided the model with respond with embeddings for contexts
     */
    query?: string;
    /**
     * List of provided contexts. Note that the index in this array is important, as the response will refer to it.
     */
    contexts: {
        /**
         * One of the provided context content
         */
        text?: string;
    }[];
    /**
     * When provided with too long context should the model error out or truncate the context to fit?
     */
    truncate_inputs?: boolean;
}
interface BGEM3InputEmbedding {
    text: string | string[];
    /**
     * When provided with too long context should the model error out or truncate the context to fit?
     */
    truncate_inputs?: boolean;
}
interface BGEM3InputQueryAndContexts1 {
    /**
     * A query you wish to perform against the provided contexts. If no query is provided the model with respond with embeddings for contexts
     */
    query?: string;
    /**
     * List of provided contexts. Note that the index in this array is important, as the response will refer to it.
     */
    contexts: {
        /**
         * One of the provided context content
         */
        text?: string;
    }[];
    /**
     * When provided with too long context should the model error out or truncate the context to fit?
     */
    truncate_inputs?: boolean;
}
interface BGEM3InputEmbedding1 {
    text: string | string[];
    /**
     * When provided with too long context should the model error out or truncate the context to fit?
     */
    truncate_inputs?: boolean;
}
type Ai_Cf_Baai_Bge_M3_Output = BGEM3OuputQuery | BGEM3OutputEmbeddingForContexts | BGEM3OuputEmbedding | AsyncResponse;
interface BGEM3OuputQuery {
    response?: {
        /**
         * Index of the context in the request
         */
        id?: number;
        /**
         * Score of the context under the index.
         */
        score?: number;
    }[];
}
interface BGEM3OutputEmbeddingForContexts {
    response?: number[][];
    shape?: number[];
    /**
     * The pooling method used in the embedding process.
     */
    pooling?: "mean" | "cls";
}
interface BGEM3OuputEmbedding {
    shape?: number[];
    /**
     * Embeddings of the requested text values
     */
    data?: number[][];
    /**
     * The pooling method used in the embedding process.
     */
    pooling?: "mean" | "cls";
}
declare abstract class Base_Ai_Cf_Baai_Bge_M3 {
    inputs: Ai_Cf_Baai_Bge_M3_Input;
    postProcessedOutputs: Ai_Cf_Baai_Bge_M3_Output;
}
interface Ai_Cf_Black_Forest_Labs_Flux_1_Schnell_Input {
    /**
     * A text description of the image you want to generate.
     */
    prompt: string;
    /**
     * The number of diffusion steps; higher values can improve quality but take longer.
     */
    steps?: number;
}
interface Ai_Cf_Black_Forest_Labs_Flux_1_Schnell_Output {
    /**
     * The generated image in Base64 format.
     */
    image?: string;
}
declare abstract class Base_Ai_Cf_Black_Forest_Labs_Flux_1_Schnell {
    inputs: Ai_Cf_Black_Forest_Labs_Flux_1_Schnell_Input;
    postProcessedOutputs: Ai_Cf_Black_Forest_Labs_Flux_1_Schnell_Output;
}
type Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct_Input = Prompt | Messages;
interface Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    image?: number[] | (string & NonNullable<unknown>);
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
    /**
     * Name of the LoRA (Low-Rank Adaptation) model to fine-tune the base model.
     */
    lora?: string;
}
interface Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role?: string;
        /**
         * The tool call id. Must be supplied for tool calls for Mistral-3. If you don't know what to put here you can fall back to 000000001
         */
        tool_call_id?: string;
        content?: string | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        }[] | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        };
    }[];
    image?: number[] | (string & NonNullable<unknown>);
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    /**
     * If true, the response will be streamed back incrementally.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Controls the creativity of the AI's responses by adjusting how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct_Output = {
    /**
     * The generated text response from the model
     */
    response?: string;
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
};
declare abstract class Base_Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct {
    inputs: Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct_Input;
    postProcessedOutputs: Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct_Output;
}
type Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Input = Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Prompt | Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Messages | AsyncBatch;
interface Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * Name of the LoRA (Low-Rank Adaptation) model to fine-tune the base model.
     */
    lora?: string;
    response_format?: JSONMode;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface JSONMode {
    type?: "json_object" | "json_schema";
    json_schema?: unknown;
}
interface Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role: string;
        /**
         * The content of the message as a string.
         */
        content: string;
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    response_format?: JSONMode;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface AsyncBatch {
    requests?: {
        /**
         * User-supplied reference. This field will be present in the response as well it can be used to reference the request and response. It's NOT validated to be unique.
         */
        external_reference?: string;
        /**
         * Prompt for the text generation model
         */
        prompt?: string;
        /**
         * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
         */
        stream?: boolean;
        /**
         * The maximum number of tokens to generate in the response.
         */
        max_tokens?: number;
        /**
         * Controls the randomness of the output; higher values produce more random results.
         */
        temperature?: number;
        /**
         * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
         */
        top_p?: number;
        /**
         * Random seed for reproducibility of the generation.
         */
        seed?: number;
        /**
         * Penalty for repeated tokens; higher values discourage repetition.
         */
        repetition_penalty?: number;
        /**
         * Decreases the likelihood of the model repeating the same lines verbatim.
         */
        frequency_penalty?: number;
        /**
         * Increases the likelihood of the model introducing new topics.
         */
        presence_penalty?: number;
        response_format?: JSONMode;
    }[];
}
type Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
} | AsyncResponse;
declare abstract class Base_Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast {
    inputs: Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Input;
    postProcessedOutputs: Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast_Output;
}
interface Ai_Cf_Meta_Llama_Guard_3_8B_Input {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender must alternate between 'user' and 'assistant'.
         */
        role: "user" | "assistant";
        /**
         * The content of the message as a string.
         */
        content: string;
    }[];
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Dictate the output format of the generated response.
     */
    response_format?: {
        /**
         * Set to json_object to process and output generated text as JSON.
         */
        type?: string;
    };
}
interface Ai_Cf_Meta_Llama_Guard_3_8B_Output {
    response?: string | {
        /**
         * Whether the conversation is safe or not.
         */
        safe?: boolean;
        /**
         * A list of what hazard categories predicted for the conversation, if the conversation is deemed unsafe.
         */
        categories?: string[];
    };
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
}
declare abstract class Base_Ai_Cf_Meta_Llama_Guard_3_8B {
    inputs: Ai_Cf_Meta_Llama_Guard_3_8B_Input;
    postProcessedOutputs: Ai_Cf_Meta_Llama_Guard_3_8B_Output;
}
interface Ai_Cf_Baai_Bge_Reranker_Base_Input {
    /**
     * A query you wish to perform against the provided contexts.
     */
    query: string;
    /**
     * Number of returned results starting with the best score.
     */
    top_k?: number;
    /**
     * List of provided contexts. Note that the index in this array is important, as the response will refer to it.
     */
    contexts: {
        /**
         * One of the provided context content
         */
        text?: string;
    }[];
}
interface Ai_Cf_Baai_Bge_Reranker_Base_Output {
    response?: {
        /**
         * Index of the context in the request
         */
        id?: number;
        /**
         * Score of the context under the index.
         */
        score?: number;
    }[];
}
declare abstract class Base_Ai_Cf_Baai_Bge_Reranker_Base {
    inputs: Ai_Cf_Baai_Bge_Reranker_Base_Input;
    postProcessedOutputs: Ai_Cf_Baai_Bge_Reranker_Base_Output;
}
type Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct_Input = Qwen2_5_Coder_32B_Instruct_Prompt | Qwen2_5_Coder_32B_Instruct_Messages;
interface Qwen2_5_Coder_32B_Instruct_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * Name of the LoRA (Low-Rank Adaptation) model to fine-tune the base model.
     */
    lora?: string;
    response_format?: JSONMode;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface Qwen2_5_Coder_32B_Instruct_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role: string;
        /**
         * The content of the message as a string.
         */
        content: string;
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    response_format?: JSONMode;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
};
declare abstract class Base_Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct {
    inputs: Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct_Input;
    postProcessedOutputs: Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct_Output;
}
type Ai_Cf_Qwen_Qwq_32B_Input = Qwen_Qwq_32B_Prompt | Qwen_Qwq_32B_Messages;
interface Qwen_Qwq_32B_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * JSON schema that should be fulfilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface Qwen_Qwq_32B_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role?: string;
        /**
         * The tool call id. Must be supplied for tool calls for Mistral-3. If you don't know what to put here you can fall back to 000000001
         */
        tool_call_id?: string;
        content?: string | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        }[] | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        };
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    /**
     * JSON schema that should be fufilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Qwen_Qwq_32B_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
};
declare abstract class Base_Ai_Cf_Qwen_Qwq_32B {
    inputs: Ai_Cf_Qwen_Qwq_32B_Input;
    postProcessedOutputs: Ai_Cf_Qwen_Qwq_32B_Output;
}
type Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct_Input = Mistral_Small_3_1_24B_Instruct_Prompt | Mistral_Small_3_1_24B_Instruct_Messages;
interface Mistral_Small_3_1_24B_Instruct_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * JSON schema that should be fulfilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface Mistral_Small_3_1_24B_Instruct_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role?: string;
        /**
         * The tool call id. Must be supplied for tool calls for Mistral-3. If you don't know what to put here you can fall back to 000000001
         */
        tool_call_id?: string;
        content?: string | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        }[] | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        };
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    /**
     * JSON schema that should be fufilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
};
declare abstract class Base_Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct {
    inputs: Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct_Input;
    postProcessedOutputs: Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct_Output;
}
type Ai_Cf_Google_Gemma_3_12B_It_Input = Google_Gemma_3_12B_It_Prompt | Google_Gemma_3_12B_It_Messages;
interface Google_Gemma_3_12B_It_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * JSON schema that should be fufilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface Google_Gemma_3_12B_It_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role?: string;
        content?: string | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        }[] | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        };
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    /**
     * JSON schema that should be fufilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Google_Gemma_3_12B_It_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The arguments passed to be passed to the tool call request
         */
        arguments?: object;
        /**
         * The name of the tool to be called
         */
        name?: string;
    }[];
};
declare abstract class Base_Ai_Cf_Google_Gemma_3_12B_It {
    inputs: Ai_Cf_Google_Gemma_3_12B_It_Input;
    postProcessedOutputs: Ai_Cf_Google_Gemma_3_12B_It_Output;
}
type Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct_Input = Ai_Cf_Meta_Llama_4_Prompt | Ai_Cf_Meta_Llama_4_Messages;
interface Ai_Cf_Meta_Llama_4_Prompt {
    /**
     * The input text prompt for the model to generate a response.
     */
    prompt: string;
    /**
     * JSON schema that should be fulfilled for the response.
     */
    guided_json?: object;
    response_format?: JSONMode;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
interface Ai_Cf_Meta_Llama_4_Messages {
    /**
     * An array of message objects representing the conversation history.
     */
    messages: {
        /**
         * The role of the message sender (e.g., 'user', 'assistant', 'system', 'tool').
         */
        role?: string;
        /**
         * The tool call id. If you don't know what to put here you can fall back to 000000001
         */
        tool_call_id?: string;
        content?: string | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        }[] | {
            /**
             * Type of the content provided
             */
            type?: string;
            text?: string;
            image_url?: {
                /**
                 * image uri with data (e.g. data:image/jpeg;base64,/9j/...). HTTP URL will not be accepted
                 */
                url?: string;
            };
        };
    }[];
    functions?: {
        name: string;
        code: string;
    }[];
    /**
     * A list of tools available for the assistant to use.
     */
    tools?: ({
        /**
         * The name of the tool. More descriptive the better.
         */
        name: string;
        /**
         * A brief description of what the tool does.
         */
        description: string;
        /**
         * Schema defining the parameters accepted by the tool.
         */
        parameters: {
            /**
             * The type of the parameters object (usually 'object').
             */
            type: string;
            /**
             * List of required parameter names.
             */
            required?: string[];
            /**
             * Definitions of each parameter.
             */
            properties: {
                [k: string]: {
                    /**
                     * The data type of the parameter.
                     */
                    type: string;
                    /**
                     * A description of the expected parameter.
                     */
                    description: string;
                };
            };
        };
    } | {
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type: string;
        /**
         * Details of the function tool.
         */
        function: {
            /**
             * The name of the function.
             */
            name: string;
            /**
             * A brief description of what the function does.
             */
            description: string;
            /**
             * Schema defining the parameters accepted by the function.
             */
            parameters: {
                /**
                 * The type of the parameters object (usually 'object').
                 */
                type: string;
                /**
                 * List of required parameter names.
                 */
                required?: string[];
                /**
                 * Definitions of each parameter.
                 */
                properties: {
                    [k: string]: {
                        /**
                         * The data type of the parameter.
                         */
                        type: string;
                        /**
                         * A description of the expected parameter.
                         */
                        description: string;
                    };
                };
            };
        };
    })[];
    response_format?: JSONMode;
    /**
     * JSON schema that should be fufilled for the response.
     */
    guided_json?: object;
    /**
     * If true, a chat template is not applied and you must adhere to the specific model's expected formatting.
     */
    raw?: boolean;
    /**
     * If true, the response will be streamed back incrementally using SSE, Server Sent Events.
     */
    stream?: boolean;
    /**
     * The maximum number of tokens to generate in the response.
     */
    max_tokens?: number;
    /**
     * Controls the randomness of the output; higher values produce more random results.
     */
    temperature?: number;
    /**
     * Adjusts the creativity of the AI's responses by controlling how many possible words it considers. Lower values make outputs more predictable; higher values allow for more varied and creative responses.
     */
    top_p?: number;
    /**
     * Limits the AI to choose from the top 'k' most probable words. Lower values make responses more focused; higher values introduce more variety and potential surprises.
     */
    top_k?: number;
    /**
     * Random seed for reproducibility of the generation.
     */
    seed?: number;
    /**
     * Penalty for repeated tokens; higher values discourage repetition.
     */
    repetition_penalty?: number;
    /**
     * Decreases the likelihood of the model repeating the same lines verbatim.
     */
    frequency_penalty?: number;
    /**
     * Increases the likelihood of the model introducing new topics.
     */
    presence_penalty?: number;
}
type Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct_Output = {
    /**
     * The generated text response from the model
     */
    response: string;
    /**
     * Usage statistics for the inference request
     */
    usage?: {
        /**
         * Total number of tokens in input
         */
        prompt_tokens?: number;
        /**
         * Total number of tokens in output
         */
        completion_tokens?: number;
        /**
         * Total number of input and output tokens
         */
        total_tokens?: number;
    };
    /**
     * An array of tool calls requests made during the response generation
     */
    tool_calls?: {
        /**
         * The tool call id.
         */
        id?: string;
        /**
         * Specifies the type of tool (e.g., 'function').
         */
        type?: string;
        /**
         * Details of the function tool.
         */
        function?: {
            /**
             * The name of the tool to be called
             */
            name?: string;
            /**
             * The arguments passed to be passed to the tool call request
             */
            arguments?: object;
        };
    }[];
};
declare abstract class Base_Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct {
    inputs: Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct_Input;
    postProcessedOutputs: Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct_Output;
}
interface AiModels {
    "@cf/huggingface/distilbert-sst-2-int8": BaseAiTextClassification;
    "@cf/stabilityai/stable-diffusion-xl-base-1.0": BaseAiTextToImage;
    "@cf/runwayml/stable-diffusion-v1-5-inpainting": BaseAiTextToImage;
    "@cf/runwayml/stable-diffusion-v1-5-img2img": BaseAiTextToImage;
    "@cf/lykon/dreamshaper-8-lcm": BaseAiTextToImage;
    "@cf/bytedance/stable-diffusion-xl-lightning": BaseAiTextToImage;
    "@cf/myshell-ai/melotts": BaseAiTextToSpeech;
    "@cf/microsoft/resnet-50": BaseAiImageClassification;
    "@cf/facebook/detr-resnet-50": BaseAiObjectDetection;
    "@cf/meta/llama-2-7b-chat-int8": BaseAiTextGeneration;
    "@cf/mistral/mistral-7b-instruct-v0.1": BaseAiTextGeneration;
    "@cf/meta/llama-2-7b-chat-fp16": BaseAiTextGeneration;
    "@hf/thebloke/llama-2-13b-chat-awq": BaseAiTextGeneration;
    "@hf/thebloke/mistral-7b-instruct-v0.1-awq": BaseAiTextGeneration;
    "@hf/thebloke/zephyr-7b-beta-awq": BaseAiTextGeneration;
    "@hf/thebloke/openhermes-2.5-mistral-7b-awq": BaseAiTextGeneration;
    "@hf/thebloke/neural-chat-7b-v3-1-awq": BaseAiTextGeneration;
    "@hf/thebloke/llamaguard-7b-awq": BaseAiTextGeneration;
    "@hf/thebloke/deepseek-coder-6.7b-base-awq": BaseAiTextGeneration;
    "@hf/thebloke/deepseek-coder-6.7b-instruct-awq": BaseAiTextGeneration;
    "@cf/deepseek-ai/deepseek-math-7b-instruct": BaseAiTextGeneration;
    "@cf/defog/sqlcoder-7b-2": BaseAiTextGeneration;
    "@cf/openchat/openchat-3.5-0106": BaseAiTextGeneration;
    "@cf/tiiuae/falcon-7b-instruct": BaseAiTextGeneration;
    "@cf/thebloke/discolm-german-7b-v1-awq": BaseAiTextGeneration;
    "@cf/qwen/qwen1.5-0.5b-chat": BaseAiTextGeneration;
    "@cf/qwen/qwen1.5-7b-chat-awq": BaseAiTextGeneration;
    "@cf/qwen/qwen1.5-14b-chat-awq": BaseAiTextGeneration;
    "@cf/tinyllama/tinyllama-1.1b-chat-v1.0": BaseAiTextGeneration;
    "@cf/microsoft/phi-2": BaseAiTextGeneration;
    "@cf/qwen/qwen1.5-1.8b-chat": BaseAiTextGeneration;
    "@cf/mistral/mistral-7b-instruct-v0.2-lora": BaseAiTextGeneration;
    "@hf/nousresearch/hermes-2-pro-mistral-7b": BaseAiTextGeneration;
    "@hf/nexusflow/starling-lm-7b-beta": BaseAiTextGeneration;
    "@hf/google/gemma-7b-it": BaseAiTextGeneration;
    "@cf/meta-llama/llama-2-7b-chat-hf-lora": BaseAiTextGeneration;
    "@cf/google/gemma-2b-it-lora": BaseAiTextGeneration;
    "@cf/google/gemma-7b-it-lora": BaseAiTextGeneration;
    "@hf/mistral/mistral-7b-instruct-v0.2": BaseAiTextGeneration;
    "@cf/meta/llama-3-8b-instruct": BaseAiTextGeneration;
    "@cf/fblgit/una-cybertron-7b-v2-bf16": BaseAiTextGeneration;
    "@cf/meta/llama-3-8b-instruct-awq": BaseAiTextGeneration;
    "@hf/meta-llama/meta-llama-3-8b-instruct": BaseAiTextGeneration;
    "@cf/meta/llama-3.1-8b-instruct": BaseAiTextGeneration;
    "@cf/meta/llama-3.1-8b-instruct-fp8": BaseAiTextGeneration;
    "@cf/meta/llama-3.1-8b-instruct-awq": BaseAiTextGeneration;
    "@cf/meta/llama-3.2-3b-instruct": BaseAiTextGeneration;
    "@cf/meta/llama-3.2-1b-instruct": BaseAiTextGeneration;
    "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b": BaseAiTextGeneration;
    "@cf/facebook/bart-large-cnn": BaseAiSummarization;
    "@cf/llava-hf/llava-1.5-7b-hf": BaseAiImageToText;
    "@cf/baai/bge-base-en-v1.5": Base_Ai_Cf_Baai_Bge_Base_En_V1_5;
    "@cf/openai/whisper": Base_Ai_Cf_Openai_Whisper;
    "@cf/meta/m2m100-1.2b": Base_Ai_Cf_Meta_M2M100_1_2B;
    "@cf/baai/bge-small-en-v1.5": Base_Ai_Cf_Baai_Bge_Small_En_V1_5;
    "@cf/baai/bge-large-en-v1.5": Base_Ai_Cf_Baai_Bge_Large_En_V1_5;
    "@cf/unum/uform-gen2-qwen-500m": Base_Ai_Cf_Unum_Uform_Gen2_Qwen_500M;
    "@cf/openai/whisper-tiny-en": Base_Ai_Cf_Openai_Whisper_Tiny_En;
    "@cf/openai/whisper-large-v3-turbo": Base_Ai_Cf_Openai_Whisper_Large_V3_Turbo;
    "@cf/baai/bge-m3": Base_Ai_Cf_Baai_Bge_M3;
    "@cf/black-forest-labs/flux-1-schnell": Base_Ai_Cf_Black_Forest_Labs_Flux_1_Schnell;
    "@cf/meta/llama-3.2-11b-vision-instruct": Base_Ai_Cf_Meta_Llama_3_2_11B_Vision_Instruct;
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast": Base_Ai_Cf_Meta_Llama_3_3_70B_Instruct_Fp8_Fast;
    "@cf/meta/llama-guard-3-8b": Base_Ai_Cf_Meta_Llama_Guard_3_8B;
    "@cf/baai/bge-reranker-base": Base_Ai_Cf_Baai_Bge_Reranker_Base;
    "@cf/qwen/qwen2.5-coder-32b-instruct": Base_Ai_Cf_Qwen_Qwen2_5_Coder_32B_Instruct;
    "@cf/qwen/qwq-32b": Base_Ai_Cf_Qwen_Qwq_32B;
    "@cf/mistralai/mistral-small-3.1-24b-instruct": Base_Ai_Cf_Mistralai_Mistral_Small_3_1_24B_Instruct;
    "@cf/google/gemma-3-12b-it": Base_Ai_Cf_Google_Gemma_3_12B_It;
    "@cf/meta/llama-4-scout-17b-16e-instruct": Base_Ai_Cf_Meta_Llama_4_Scout_17B_16E_Instruct;
}
type AiOptions = {
    /**
     * Send requests as an asynchronous batch job, only works for supported models
     * https://developers.cloudflare.com/workers-ai/features/batch-api
     */
    queueRequest?: boolean;
    gateway?: GatewayOptions;
    returnRawResponse?: boolean;
    prefix?: string;
    extraHeaders?: object;
};
type ConversionResponse = {
    name: string;
    mimeType: string;
    format: "markdown";
    tokens: number;
    data: string;
};
type AiModelsSearchParams = {
    author?: string;
    hide_experimental?: boolean;
    page?: number;
    per_page?: number;
    search?: string;
    source?: number;
    task?: string;
};
type AiModelsSearchObject = {
    id: string;
    source: number;
    name: string;
    description: string;
    task: {
        id: string;
        name: string;
        description: string;
    };
    tags: string[];
    properties: {
        property_id: string;
        value: string;
    }[];
};
interface InferenceUpstreamError extends Error {
}
interface AiInternalError extends Error {
}
type AiModelListType = Record<string, any>;
declare abstract class Ai<AiModelList extends AiModelListType = AiModels> {
    aiGatewayLogId: string | null;
    gateway(gatewayId: string): AiGateway;
    autorag(autoragId?: string): AutoRAG;
    run<Name extends keyof AiModelList, Options extends AiOptions, InputOptions extends AiModelList[Name]["inputs"]>(model: Name, inputs: InputOptions, options?: Options): Promise<Options extends {
        returnRawResponse: true;
    } ? Response : InputOptions extends {
        stream: true;
    } ? ReadableStream : AiModelList[Name]["postProcessedOutputs"]>;
    models(params?: AiModelsSearchParams): Promise<AiModelsSearchObject[]>;
    toMarkdown(files: {
        name: string;
        blob: Blob;
    }[], options?: {
        gateway?: GatewayOptions;
        extraHeaders?: object;
    }): Promise<ConversionResponse[]>;
    toMarkdown(files: {
        name: string;
        blob: Blob;
    }, options?: {
        gateway?: GatewayOptions;
        extraHeaders?: object;
    }): Promise<ConversionResponse>;
}
type GatewayRetries = {
    maxAttempts?: 1 | 2 | 3 | 4 | 5;
    retryDelayMs?: number;
    backoff?: 'constant' | 'linear' | 'exponential';
};
type GatewayOptions = {
    id: string;
    cacheKey?: string;
    cacheTtl?: number;
    skipCache?: boolean;
    metadata?: Record<string, number | string | boolean | null | bigint>;
    collectLog?: boolean;
    eventId?: string;
    requestTimeoutMs?: number;
    retries?: GatewayRetries;
};
type AiGatewayPatchLog = {
    score?: number | null;
    feedback?: -1 | 1 | null;
    metadata?: Record<string, number | string | boolean | null | bigint> | null;
};
type AiGatewayLog = {
    id: string;
    provider: string;
    model: string;
    model_type?: string;
    path: string;
    duration: number;
    request_type?: string;
    request_content_type?: string;
    status_code: number;
    response_content_type?: string;
    success: boolean;
    cached: boolean;
    tokens_in?: number;
    tokens_out?: number;
    metadata?: Record<string, number | string | boolean | null | bigint>;
    step?: number;
    cost?: number;
    custom_cost?: boolean;
    request_size: number;
    request_head?: string;
    request_head_complete: boolean;
    response_size: number;
    response_head?: string;
    response_head_complete: boolean;
    created_at: Date;
};
type AIGatewayProviders = 'workers-ai' | 'anthropic' | 'aws-bedrock' | 'azure-openai' | 'google-vertex-ai' | 'huggingface' | 'openai' | 'perplexity-ai' | 'replicate' | 'groq' | 'cohere' | 'google-ai-studio' | 'mistral' | 'grok' | 'openrouter' | 'deepseek' | 'cerebras' | 'cartesia' | 'elevenlabs' | 'adobe-firefly';
type AIGatewayHeaders = {
    'cf-aig-metadata': Record<string, number | string | boolean | null | bigint> | string;
    'cf-aig-custom-cost': {
        per_token_in?: number;
        per_token_out?: number;
    } | {
        total_cost?: number;
    } | string;
    'cf-aig-cache-ttl': number | string;
    'cf-aig-skip-cache': boolean | string;
    'cf-aig-cache-key': string;
    'cf-aig-event-id': string;
    'cf-aig-request-timeout': number | string;
    'cf-aig-max-attempts': number | string;
    'cf-aig-retry-delay': number | string;
    'cf-aig-backoff': string;
    'cf-aig-collect-log': boolean | string;
    Authorization: string;
    'Content-Type': string;
    [key: string]: string | number | boolean | object;
};
type AIGatewayUniversalRequest = {
    provider: AIGatewayProviders | string; // eslint-disable-line
    endpoint: string;
    headers: Partial<AIGatewayHeaders>;
    query: unknown;
};
interface AiGatewayInternalError extends Error {
}
interface AiGatewayLogNotFound extends Error {
}
declare abstract class AiGateway {
    patchLog(logId: string, data: AiGatewayPatchLog): Promise<void>;
    getLog(logId: string): Promise<AiGatewayLog>;
    run(data: AIGatewayUniversalRequest | AIGatewayUniversalRequest[], options?: {
        gateway?: GatewayOptions;
        extraHeaders?: object;
    }): Promise<Response>;
    getUrl(provider?: AIGatewayProviders | string): Promise<string>; // eslint-disable-line
}
interface AutoRAGInternalError extends Error {
}
interface AutoRAGNotFoundError extends Error {
}
interface AutoRAGUnauthorizedError extends Error {
}
interface AutoRAGNameNotSetError extends Error {
}
type ComparisonFilter = {
    key: string;
    type: 'eq' | 'ne' | 'gt' | 'gte' | 'lt' | 'lte';
    value: string | number | boolean;
};
type CompoundFilter = {
    type: 'and' | 'or';
    filters: ComparisonFilter[];
};
type AutoRagSearchRequest = {
    query: string;
    filters?: CompoundFilter | ComparisonFilter;
    max_num_results?: number;
    ranking_options?: {
        ranker?: string;
        score_threshold?: number;
    };
    rewrite_query?: boolean;
};
type AutoRagAiSearchRequest = AutoRagSearchRequest & {
    stream?: boolean;
};
type AutoRagAiSearchRequestStreaming = Omit<AutoRagAiSearchRequest, 'stream'> & {
    stream: true;
};
type AutoRagSearchResponse = {
    object: 'vector_store.search_results.page';
    search_query: string;
    data: {
        file_id: string;
        filename: string;
        score: number;
        attributes: Record<string, string | number | boolean | null>;
        content: {
            type: 'text';
            text: string;
        }[];
    }[];
    has_more: boolean;
    next_page: string | null;
};
type AutoRagListResponse = {
    id: string;
    enable: boolean;
    type: string;
    source: string;
    vectorize_name: string;
    paused: boolean;
    status: string;
}[];
type AutoRagAiSearchResponse = AutoRagSearchResponse & {
    response: string;
};
declare abstract class AutoRAG {
    list(): Promise<AutoRagListResponse>;
    search(params: AutoRagSearchRequest): Promise<AutoRagSearchResponse>;
    aiSearch(params: AutoRagAiSearchRequestStreaming): Promise<Response>;
    aiSearch(params: AutoRagAiSearchRequest): Promise<AutoRagAiSearchResponse>;
    aiSearch(params: AutoRagAiSearchRequest): Promise<AutoRagAiSearchResponse | Response>;
}
interface BasicImageTransformations {
    /**
     * Maximum width in image pixels. The value must be an integer.
     */
    width?: number;
    /**
     * Maximum height in image pixels. The value must be an integer.
     */
    height?: number;
    /**
     * Resizing mode as a string. It affects interpretation of width and height
     * options:
     *  - scale-down: Similar to contain, but the image is never enlarged. If
     *    the image is larger than given width or height, it will be resized.
     *    Otherwise its original size will be kept.
     *  - contain: Resizes to maximum size that fits within the given width and
     *    height. If only a single dimension is given (e.g. only width), the
     *    image will be shrunk or enlarged to exactly match that dimension.
     *    Aspect ratio is always preserved.
     *  - cover: Resizes (shrinks or enlarges) to fill the entire area of width
     *    and height. If the image has an aspect ratio different from the ratio
     *    of width and height, it will be cropped to fit.
     *  - crop: The image will be shrunk and cropped to fit within the area
     *    specified by width and height. The image will not be enlarged. For images
     *    smaller than the given dimensions it's the same as scale-down. For
     *    images larger than the given dimensions, it's the same as cover.
     *    See also trim.
     *  - pad: Resizes to the maximum size that fits within the given width and
     *    height, and then fills the remaining area with a background color
     *    (white by default). Use of this mode is not recommended, as the same
     *    effect can be more efficiently achieved with the contain mode and the
     *    CSS object-fit: contain property.
     *  - squeeze: Stretches and deforms to the width and height given, even if it
     *    breaks aspect ratio
     */
    fit?: "scale-down" | "contain" | "cover" | "crop" | "pad" | "squeeze";
    /**
     * When cropping with fit: "cover", this defines the side or point that should
     * be left uncropped. The value is either a string
     * "left", "right", "top", "bottom", "auto", or "center" (the default),
     * or an object {x, y} containing focal point coordinates in the original
     * image expressed as fractions ranging from 0.0 (top or left) to 1.0
     * (bottom or right), 0.5 being the center. {fit: "cover", gravity: "top"} will
     * crop bottom or left and right sides as necessary, but won’t crop anything
     * from the top. {fit: "cover", gravity: {x:0.5, y:0.2}} will crop each side to
     * preserve as much as possible around a point at 20% of the height of the
     * source image.
     */
    gravity?: 'left' | 'right' | 'top' | 'bottom' | 'center' | 'auto' | 'entropy' | BasicImageTransformationsGravityCoordinates;
    /**
     * Background color to add underneath the image. Applies only to images with
     * transparency (such as PNG). Accepts any CSS color (#RRGGBB, rgba(…),
     * hsl(…), etc.)
     */
    background?: string;
    /**
     * Number of degrees (90, 180, 270) to rotate the image by. width and height
     * options refer to axes after rotation.
     */
    rotate?: 0 | 90 | 180 | 270 | 360;
}
interface BasicImageTransformationsGravityCoordinates {
    x?: number;
    y?: number;
    mode?: 'remainder' | 'box-center';
}
/**
 * In addition to the properties you can set in the RequestInit dict
 * that you pass as an argument to the Request constructor, you can
 * set certain properties of a `cf` object to control how Cloudflare
 * features are applied to that new Request.
 *
 * Note: Currently, these properties cannot be tested in the
 * playground.
 */
interface RequestInitCfProperties extends Record<string, unknown> {
    cacheEverything?: boolean;
    /**
     * A request's cache key is what determines if two requests are
     * "the same" for caching purposes. If a request has the same cache key
     * as some previous request, then we can serve the same cached response for
     * both. (e.g. 'some-key')
     *
     * Only available for Enterprise customers.
     */
    cacheKey?: string;
    /**
     * This allows you to append additional Cache-Tag response headers
     * to the origin response without modifications to the origin server.
     * This will allow for greater control over the Purge by Cache Tag feature
     * utilizing changes only in the Workers process.
     *
     * Only available for Enterprise customers.
     */
    cacheTags?: string[];
    /**
     * Force response to be cached for a given number of seconds. (e.g. 300)
     */
    cacheTtl?: number;
    /**
     * Force response to be cached for a given number of seconds based on the Origin status code.
     * (e.g. { '200-299': 86400, '404': 1, '500-599': 0 })
     */
    cacheTtlByStatus?: Record<string, number>;
    scrapeShield?: boolean;
    apps?: boolean;
    image?: RequestInitCfPropertiesImage;
    minify?: RequestInitCfPropertiesImageMinify;
    mirage?: boolean;
    polish?: "lossy" | "lossless" | "off";
    r2?: RequestInitCfPropertiesR2;
    /**
     * Redirects the request to an alternate origin server. You can use this,
     * for example, to implement load balancing across several origins.
     * (e.g.us-east.example.com)
     *
     * Note - For security reasons, the hostname set in resolveOverride must
     * be proxied on the same Cloudflare zone of the incoming request.
     * Otherwise, the setting is ignored. CNAME hosts are allowed, so to
     * resolve to a host under a different domain or a DNS only domain first
     * declare a CNAME record within your own zone’s DNS mapping to the
     * external hostname, set proxy on Cloudflare, then set resolveOverride
     * to point to that CNAME record.
     */
    resolveOverride?: string;
}
interface RequestInitCfPropertiesImageDraw extends BasicImageTransformations {
    /**
     * Absolute URL of the image file to use for the drawing. It can be any of
     * the supported file formats. For drawing of watermarks or non-rectangular
     * overlays we recommend using PNG or WebP images.
     */
    url: string;
    /**
     * Floating-point number between 0 (transparent) and 1 (opaque).
     * For example, opacity: 0.5 makes overlay semitransparent.
     */
    opacity?: number;
    /**
     * - If set to true, the overlay image will be tiled to cover the entire
     *   area. This is useful for stock-photo-like watermarks.
     * - If set to "x", the overlay image will be tiled horizontally only
     *   (form a line).
     * - If set to "y", the overlay image will be tiled vertically only
     *   (form a line).
     */
    repeat?: true | "x" | "y";
    /**
     * Position of the overlay image relative to a given edge. Each property is
     * an offset in pixels. 0 aligns exactly to the edge. For example, left: 10
     * positions left side of the overlay 10 pixels from the left edge of the
     * image it's drawn over. bottom: 0 aligns bottom of the overlay with bottom
     * of the background image.
     *
     * Setting both left & right, or both top & bottom is an error.
     *
     * If no position is specified, the image will be centered.
     */
    top?: number;
    left?: number;
    bottom?: number;
    right?: number;
}
interface RequestInitCfPropertiesImage extends BasicImageTransformations {
    /**
     * Device Pixel Ratio. Default 1. Multiplier for width/height that makes it
     * easier to specify higher-DPI sizes in <img srcset>.
     */
    dpr?: number;
    /**
     * Allows you to trim your image. Takes dpr into account and is performed before
     * resizing or rotation.
     *
     * It can be used as:
     * - left, top, right, bottom - it will specify the number of pixels to cut
     *   off each side
     * - width, height - the width/height you'd like to end up with - can be used
     *   in combination with the properties above
     * - border - this will automatically trim the surroundings of an image based on
     *   it's color. It consists of three properties:
     *    - color: rgb or hex representation of the color you wish to trim (todo: verify the rgba bit)
     *    - tolerance: difference from color to treat as color
     *    - keep: the number of pixels of border to keep
     */
    trim?: "border" | {
        top?: number;
        bottom?: number;
        left?: number;
        right?: number;
        width?: number;
        height?: number;
        border?: boolean | {
            color?: string;
            tolerance?: number;
            keep?: number;
        };
    };
    /**
     * Quality setting from 1-100 (useful values are in 60-90 range). Lower values
     * make images look worse, but load faster. The default is 85. It applies only
     * to JPEG and WebP images. It doesn’t have any effect on PNG.
     */
    quality?: number | "low" | "medium-low" | "medium-high" | "high";
    /**
     * Output format to generate. It can be:
     *  - avif: generate images in AVIF format.
     *  - webp: generate images in Google WebP format. Set quality to 100 to get
     *    the WebP-lossless format.
     *  - json: instead of generating an image, outputs information about the
     *    image, in JSON format. The JSON object will contain image size
     *    (before and after resizing), source image’s MIME type, file size, etc.
     * - jpeg: generate images in JPEG format.
     * - png: generate images in PNG format.
     */
    format?: "avif" | "webp" | "json" | "jpeg" | "png" | "baseline-jpeg" | "png-force" | "svg";
    /**
     * Whether to preserve animation frames from input files. Default is true.
     * Setting it to false reduces animations to still images. This setting is
     * recommended when enlarging images or processing arbitrary user content,
     * because large GIF animations can weigh tens or even hundreds of megabytes.
     * It is also useful to set anim:false when using format:"json" to get the
     * response quicker without the number of frames.
     */
    anim?: boolean;
    /**
     * What EXIF data should be preserved in the output image. Note that EXIF
     * rotation and embedded color profiles are always applied ("baked in" into
     * the image), and aren't affected by this option. Note that if the Polish
     * feature is enabled, all metadata may have been removed already and this
     * option may have no effect.
     *  - keep: Preserve most of EXIF metadata, including GPS location if there's
     *    any.
     *  - copyright: Only keep the copyright tag, and discard everything else.
     *    This is the default behavior for JPEG files.
     *  - none: Discard all invisible EXIF metadata. Currently WebP and PNG
     *    output formats always discard metadata.
     */
    metadata?: "keep" | "copyright" | "none";
    /**
     * Strength of sharpening filter to apply to the image. Floating-point
     * number between 0 (no sharpening, default) and 10 (maximum). 1.0 is a
     * recommended value for downscaled images.
     */
    sharpen?: number;
    /**
     * Radius of a blur filter (approximate gaussian). Maximum supported radius
     * is 250.
     */
    blur?: number;
    /**
     * Overlays are drawn in the order they appear in the array (last array
     * entry is the topmost layer).
     */
    draw?: RequestInitCfPropertiesImageDraw[];
    /**
     * Fetching image from authenticated origin. Setting this property will
     * pass authentication headers (Authorization, Cookie, etc.) through to
     * the origin.
     */
    "origin-auth"?: "share-publicly";
    /**
     * Adds a border around the image. The border is added after resizing. Border
     * width takes dpr into account, and can be specified either using a single
     * width property, or individually for each side.
     */
    border?: {
        color: string;
        width: number;
    } | {
        color: string;
        top: number;
        right: number;
        bottom: number;
        left: number;
    };
    /**
     * Increase brightness by a factor. A value of 1.0 equals no change, a value
     * of 0.5 equals half brightness, and a value of 2.0 equals twice as bright.
     * 0 is ignored.
     */
    brightness?: number;
    /**
     * Increase contrast by a factor. A value of 1.0 equals no change, a value of
     * 0.5 equals low contrast, and a value of 2.0 equals high contrast. 0 is
     * ignored.
     */
    contrast?: number;
    /**
     * Increase exposure by a factor. A value of 1.0 equals no change, a value of
     * 0.5 darkens the image, and a value of 2.0 lightens the image. 0 is ignored.
     */
    gamma?: number;
    /**
     * Increase contrast by a factor. A value of 1.0 equals no change, a value of
     * 0.5 equals low contrast, and a value of 2.0 equals high contrast. 0 is
     * ignored.
     */
    saturation?: number;
    /**
     * Flips the images horizontally, vertically, or both. Flipping is applied before
     * rotation, so if you apply flip=h,rotate=90 then the image will be flipped
     * horizontally, then rotated by 90 degrees.
     */
    flip?: 'h' | 'v' | 'hv';
    /**
     * Slightly reduces latency on a cache miss by selecting a
     * quickest-to-compress file format, at a cost of increased file size and
     * lower image quality. It will usually override the format option and choose
     * JPEG over WebP or AVIF. We do not recommend using this option, except in
     * unusual circumstances like resizing uncacheable dynamically-generated
     * images.
     */
    compression?: "fast";
}
interface RequestInitCfPropertiesImageMinify {
    javascript?: boolean;
    css?: boolean;
    html?: boolean;
}
interface RequestInitCfPropertiesR2 {
    /**
     * Colo id of bucket that an object is stored in
     */
    bucketColoId?: number;
}
/**
 * Request metadata provided by Cloudflare's edge.
 */
type IncomingRequestCfProperties<HostMetadata = unknown> = IncomingRequestCfPropertiesBase & IncomingRequestCfPropertiesBotManagementEnterprise & IncomingRequestCfPropertiesCloudflareForSaaSEnterprise<HostMetadata> & IncomingRequestCfPropertiesGeographicInformation & IncomingRequestCfPropertiesCloudflareAccessOrApiShield;
interface IncomingRequestCfPropertiesBase extends Record<string, unknown> {
    /**
     * [ASN](https://www.iana.org/assignments/as-numbers/as-numbers.xhtml) of the incoming request.
     *
     * @example 395747
     */
    asn: number;
    /**
     * The organization which owns the ASN of the incoming request.
     *
     * @example "Google Cloud"
     */
    asOrganization: string;
    /**
     * The original value of the `Accept-Encoding` header if Cloudflare modified it.
     *
     * @example "gzip, deflate, br"
     */
    clientAcceptEncoding?: string;
    /**
     * The number of milliseconds it took for the request to reach your worker.
     *
     * @example 22
     */
    clientTcpRtt?: number;
    /**
     * The three-letter [IATA](https://en.wikipedia.org/wiki/IATA_airport_code)
     * airport code of the data center that the request hit.
     *
     * @example "DFW"
     */
    colo: string;
    /**
     * Represents the upstream's response to a
     * [TCP `keepalive` message](https://tldp.org/HOWTO/TCP-Keepalive-HOWTO/overview.html)
     * from cloudflare.
     *
     * For workers with no upstream, this will always be `1`.
     *
     * @example 3
     */
    edgeRequestKeepAliveStatus: IncomingRequestCfPropertiesEdgeRequestKeepAliveStatus;
    /**
     * The HTTP Protocol the request used.
     *
     * @example "HTTP/2"
     */
    httpProtocol: string;
    /**
     * The browser-requested prioritization information in the request object.
     *
     * If no information was set, defaults to the empty string `""`
     *
     * @example "weight=192;exclusive=0;group=3;group-weight=127"
     * @default ""
     */
    requestPriority: string;
    /**
     * The TLS version of the connection to Cloudflare.
     * In requests served over plaintext (without TLS), this property is the empty string `""`.
     *
     * @example "TLSv1.3"
     */
    tlsVersion: string;
    /**
     * The cipher for the connection to Cloudflare.
     * In requests served over plaintext (without TLS), this property is the empty string `""`.
     *
     * @example "AEAD-AES128-GCM-SHA256"
     */
    tlsCipher: string;
    /**
     * Metadata containing the [`HELLO`](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.1.2) and [`FINISHED`](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.9) messages from this request's TLS handshake.
     *
     * If the incoming request was served over plaintext (without TLS) this field is undefined.
     */
    tlsExportedAuthenticator?: IncomingRequestCfPropertiesExportedAuthenticatorMetadata;
}
interface IncomingRequestCfPropertiesBotManagementBase {
    /**
     * Cloudflare’s [level of certainty](https://developers.cloudflare.com/bots/concepts/bot-score/) that a request comes from a bot,
     * represented as an integer percentage between `1` (almost certainly a bot) and `99` (almost certainly human).
     *
     * @example 54
     */
    score: number;
    /**
     * A boolean value that is true if the request comes from a good bot, like Google or Bing.
     * Most customers choose to allow this traffic. For more details, see [Traffic from known bots](https://developers.cloudflare.com/firewall/known-issues-and-faq/#how-does-firewall-rules-handle-traffic-from-known-bots).
     */
    verifiedBot: boolean;
    /**
     * A boolean value that is true if the request originates from a
     * Cloudflare-verified proxy service.
     */
    corporateProxy: boolean;
    /**
     * A boolean value that's true if the request matches [file extensions](https://developers.cloudflare.com/bots/reference/static-resources/) for many types of static resources.
     */
    staticResource: boolean;
    /**
     * List of IDs that correlate to the Bot Management heuristic detections made on a request (you can have multiple heuristic detections on the same request).
     */
    detectionIds: number[];
}
interface IncomingRequestCfPropertiesBotManagement {
    /**
     * Results of Cloudflare's Bot Management analysis
     */
    botManagement: IncomingRequestCfPropertiesBotManagementBase;
    /**
     * Duplicate of `botManagement.score`.
     *
     * @deprecated
     */
    clientTrustScore: number;
}
interface IncomingRequestCfPropertiesBotManagementEnterprise extends IncomingRequestCfPropertiesBotManagement {
    /**
     * Results of Cloudflare's Bot Management analysis
     */
    botManagement: IncomingRequestCfPropertiesBotManagementBase & {
        /**
         * A [JA3 Fingerprint](https://developers.cloudflare.com/bots/concepts/ja3-fingerprint/) to help profile specific SSL/TLS clients
         * across different destination IPs, Ports, and X509 certificates.
         */
        ja3Hash: string;
    };
}
interface IncomingRequestCfPropertiesCloudflareForSaaSEnterprise<HostMetadata> {
    /**
     * Custom metadata set per-host in [Cloudflare for SaaS](https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/).
     *
     * This field is only present if you have Cloudflare for SaaS enabled on your account
     * and you have followed the [required steps to enable it]((https://developers.cloudflare.com/cloudflare-for-platforms/cloudflare-for-saas/domain-support/custom-metadata/)).
     */
    hostMetadata: HostMetadata;
}
interface IncomingRequestCfPropertiesCloudflareAccessOrApiShield {
    /**
     * Information about the client certificate presented to Cloudflare.
     *
     * This is populated when the incoming request is served over TLS using
     * either Cloudflare Access or API Shield (mTLS)
     * and the presented SSL certificate has a valid
     * [Certificate Serial Number](https://ldapwiki.com/wiki/Certificate%20Serial%20Number)
     * (i.e., not `null` or `""`).
     *
     * Otherwise, a set of placeholder values are used.
     *
     * The property `certPresented` will be set to `"1"` when
     * the object is populated (i.e. the above conditions were met).
     */
    tlsClientAuth: IncomingRequestCfPropertiesTLSClientAuth | IncomingRequestCfPropertiesTLSClientAuthPlaceholder;
}
/**
 * Metadata about the request's TLS handshake
 */
interface IncomingRequestCfPropertiesExportedAuthenticatorMetadata {
    /**
     * The client's [`HELLO` message](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.1.2), encoded in hexadecimal
     *
     * @example "44372ba35fa1270921d318f34c12f155dc87b682cf36a790cfaa3ba8737a1b5d"
     */
    clientHandshake: string;
    /**
     * The server's [`HELLO` message](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.1.2), encoded in hexadecimal
     *
     * @example "44372ba35fa1270921d318f34c12f155dc87b682cf36a790cfaa3ba8737a1b5d"
     */
    serverHandshake: string;
    /**
     * The client's [`FINISHED` message](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.9), encoded in hexadecimal
     *
     * @example "084ee802fe1348f688220e2a6040a05b2199a761f33cf753abb1b006792d3f8b"
     */
    clientFinished: string;
    /**
     * The server's [`FINISHED` message](https://www.rfc-editor.org/rfc/rfc5246#section-7.4.9), encoded in hexadecimal
     *
     * @example "084ee802fe1348f688220e2a6040a05b2199a761f33cf753abb1b006792d3f8b"
     */
    serverFinished: string;
}
/**
 * Geographic data about the request's origin.
 */
interface IncomingRequestCfPropertiesGeographicInformation {
    /**
     * The [ISO 3166-1 Alpha 2](https://www.iso.org/iso-3166-country-codes.html) country code the request originated from.
     *
     * If your worker is [configured to accept TOR connections](https://support.cloudflare.com/hc/en-us/articles/203306930-Understanding-Cloudflare-Tor-support-and-Onion-Routing), this may also be `"T1"`, indicating a request that originated over TOR.
     *
     * If Cloudflare is unable to determine where the request originated this property is omitted.
     *
     * The country code `"T1"` is used for requests originating on TOR.
     *
     * @example "GB"
     */
    country?: Iso3166Alpha2Code | "T1";
    /**
     * If present, this property indicates that the request originated in the EU
     *
     * @example "1"
     */
    isEUCountry?: "1";
    /**
     * A two-letter code indicating the continent the request originated from.
     *
     * @example "AN"
     */
    continent?: ContinentCode;
    /**
     * The city the request originated from
     *
     * @example "Austin"
     */
    city?: string;
    /**
     * Postal code of the incoming request
     *
     * @example "78701"
     */
    postalCode?: string;
    /**
     * Latitude of the incoming request
     *
     * @example "30.27130"
     */
    latitude?: string;
    /**
     * Longitude of the incoming request
     *
     * @example "-97.74260"
     */
    longitude?: string;
    /**
     * Timezone of the incoming request
     *
     * @example "America/Chicago"
     */
    timezone?: string;
    /**
     * If known, the ISO 3166-2 name for the first level region associated with
     * the IP address of the incoming request
     *
     * @example "Texas"
     */
    region?: string;
    /**
     * If known, the ISO 3166-2 code for the first-level region associated with
     * the IP address of the incoming request
     *
     * @example "TX"
     */
    regionCode?: string;
    /**
     * Metro code (DMA) of the incoming request
     *
     * @example "635"
     */
    metroCode?: string;
}
/** Data about the incoming request's TLS certificate */
interface IncomingRequestCfPropertiesTLSClientAuth {
    /** Always `"1"`, indicating that the certificate was presented */
    certPresented: "1";
    /**
     * Result of certificate verification.
     *
     * @example "FAILED:self signed certificate"
     */
    certVerified: Exclude<CertVerificationStatus, "NONE">;
    /** The presented certificate's revokation status.
     *
     * - A value of `"1"` indicates the certificate has been revoked
     * - A value of `"0"` indicates the certificate has not been revoked
     */
    certRevoked: "1" | "0";
    /**
     * The certificate issuer's [distinguished name](https://knowledge.digicert.com/generalinformation/INFO1745.html)
     *
     * @example "CN=cloudflareaccess.com, C=US, ST=Texas, L=Austin, O=Cloudflare"
     */
    certIssuerDN: string;
    /**
     * The certificate subject's [distinguished name](https://knowledge.digicert.com/generalinformation/INFO1745.html)
     *
     * @example "CN=*.cloudflareaccess.com, C=US, ST=Texas, L=Austin, O=Cloudflare"
     */
    certSubjectDN: string;
    /**
     * The certificate issuer's [distinguished name](https://knowledge.digicert.com/generalinformation/INFO1745.html) ([RFC 2253](https://www.rfc-editor.org/rfc/rfc2253.html) formatted)
     *
     * @example "CN=cloudflareaccess.com, C=US, ST=Texas, L=Austin, O=Cloudflare"
     */
    certIssuerDNRFC2253: string;
    /**
     * The certificate subject's [distinguished name](https://knowledge.digicert.com/generalinformation/INFO1745.html) ([RFC 2253](https://www.rfc-editor.org/rfc/rfc2253.html) formatted)
     *
     * @example "CN=*.cloudflareaccess.com, C=US, ST=Texas, L=Austin, O=Cloudflare"
     */
    certSubjectDNRFC2253: string;
    /** The certificate issuer's distinguished name (legacy policies) */
    certIssuerDNLegacy: string;
    /** The certificate subject's distinguished name (legacy policies) */
    certSubjectDNLegacy: string;
    /**
     * The certificate's serial number
     *
     * @example "00936EACBE07F201DF"
     */
    certSerial: string;
    /**
     * The certificate issuer's serial number
     *
     * @example "2489002934BDFEA34"
     */
    certIssuerSerial: string;
    /**
     * The certificate's Subject Key Identifier
     *
     * @example "BB:AF:7E:02:3D:FA:A6:F1:3C:84:8E:AD:EE:38:98:EC:D9:32:32:D4"
     */
    certSKI: string;
    /**
     * The certificate issuer's Subject Key Identifier
     *
     * @example "BB:AF:7E:02:3D:FA:A6:F1:3C:84:8E:AD:EE:38:98:EC:D9:32:32:D4"
     */
    certIssuerSKI: string;
    /**
     * The certificate's SHA-1 fingerprint
     *
     * @example "6b9109f323999e52259cda7373ff0b4d26bd232e"
     */
    certFingerprintSHA1: string;
    /**
     * The certificate's SHA-256 fingerprint
     *
     * @example "acf77cf37b4156a2708e34c4eb755f9b5dbbe5ebb55adfec8f11493438d19e6ad3f157f81fa3b98278453d5652b0c1fd1d71e5695ae4d709803a4d3f39de9dea"
     */
    certFingerprintSHA256: string;
    /**
     * The effective starting date of the certificate
     *
     * @example "Dec 22 19:39:00 2018 GMT"
     */
    certNotBefore: string;
    /**
     * The effective expiration date of the certificate
     *
     * @example "Dec 22 19:39:00 2018 GMT"
     */
    certNotAfter: string;
}
/** Placeholder values for TLS Client Authorization */
interface IncomingRequestCfPropertiesTLSClientAuthPlaceholder {
    certPresented: "0";
    certVerified: "NONE";
    certRevoked: "0";
    certIssuerDN: "";
    certSubjectDN: "";
    certIssuerDNRFC2253: "";
    certSubjectDNRFC2253: "";
    certIssuerDNLegacy: "";
    certSubjectDNLegacy: "";
    certSerial: "";
    certIssuerSerial: "";
    certSKI: "";
    certIssuerSKI: "";
    certFingerprintSHA1: "";
    certFingerprintSHA256: "";
    certNotBefore: "";
    certNotAfter: "";
}
/** Possible outcomes of TLS verification */
declare type CertVerificationStatus = 
/** Authentication succeeded */
"SUCCESS"
/** No certificate was presented */
 | "NONE"
/** Failed because the certificate was self-signed */
 | "FAILED:self signed certificate"
/** Failed because the certificate failed a trust chain check */
 | "FAILED:unable to verify the first certificate"
/** Failed because the certificate not yet valid */
 | "FAILED:certificate is not yet valid"
/** Failed because the certificate is expired */
 | "FAILED:certificate has expired"
/** Failed for another unspecified reason */
 | "FAILED";
/**
 * An upstream endpoint's response to a TCP `keepalive` message from Cloudflare.
 */
declare type IncomingRequestCfPropertiesEdgeRequestKeepAliveStatus = 0 /** Unknown */ | 1 /** no keepalives (not found) */ | 2 /** no connection re-use, opening keepalive connection failed */ | 3 /** no connection re-use, keepalive accepted and saved */ | 4 /** connection re-use, refused by the origin server (`TCP FIN`) */ | 5; /** connection re-use, accepted by the origin server */
/** ISO 3166-1 Alpha-2 codes */
declare type Iso3166Alpha2Code = "AD" | "AE" | "AF" | "AG" | "AI" | "AL" | "AM" | "AO" | "AQ" | "AR" | "AS" | "AT" | "AU" | "AW" | "AX" | "AZ" | "BA" | "BB" | "BD" | "BE" | "BF" | "BG" | "BH" | "BI" | "BJ" | "BL" | "BM" | "BN" | "BO" | "BQ" | "BR" | "BS" | "BT" | "BV" | "BW" | "BY" | "BZ" | "CA" | "CC" | "CD" | "CF" | "CG" | "CH" | "CI" | "CK" | "CL" | "CM" | "CN" | "CO" | "CR" | "CU" | "CV" | "CW" | "CX" | "CY" | "CZ" | "DE" | "DJ" | "DK" | "DM" | "DO" | "DZ" | "EC" | "EE" | "EG" | "EH" | "ER" | "ES" | "ET" | "FI" | "FJ" | "FK" | "FM" | "FO" | "FR" | "GA" | "GB" | "GD" | "GE" | "GF" | "GG" | "GH" | "GI" | "GL" | "GM" | "GN" | "GP" | "GQ" | "GR" | "GS" | "GT" | "GU" | "GW" | "GY" | "HK" | "HM" | "HN" | "HR" | "HT" | "HU" | "ID" | "IE" | "IL" | "IM" | "IN" | "IO" | "IQ" | "IR" | "IS" | "IT" | "JE" | "JM" | "JO" | "JP" | "KE" | "KG" | "KH" | "KI" | "KM" | "KN" | "KP" | "KR" | "KW" | "KY" | "KZ" | "LA" | "LB" | "LC" | "LI" | "LK" | "LR" | "LS" | "LT" | "LU" | "LV" | "LY" | "MA" | "MC" | "MD" | "ME" | "MF" | "MG" | "MH" | "MK" | "ML" | "MM" | "MN" | "MO" | "MP" | "MQ" | "MR" | "MS" | "MT" | "MU" | "MV" | "MW" | "MX" | "MY" | "MZ" | "NA" | "NC" | "NE" | "NF" | "NG" | "NI" | "NL" | "NO" | "NP" | "NR" | "NU" | "NZ" | "OM" | "PA" | "PE" | "PF" | "PG" | "PH" | "PK" | "PL" | "PM" | "PN" | "PR" | "PS" | "PT" | "PW" | "PY" | "QA" | "RE" | "RO" | "RS" | "RU" | "RW" | "SA" | "SB" | "SC" | "SD" | "SE" | "SG" | "SH" | "SI" | "SJ" | "SK" | "SL" | "SM" | "SN" | "SO" | "SR" | "SS" | "ST" | "SV" | "SX" | "SY" | "SZ" | "TC" | "TD" | "TF" | "TG" | "TH" | "TJ" | "TK" | "TL" | "TM" | "TN" | "TO" | "TR" | "TT" | "TV" | "TW" | "TZ" | "UA" | "UG" | "UM" | "US" | "UY" | "UZ" | "VA" | "VC" | "VE" | "VG" | "VI" | "VN" | "VU" | "WF" | "WS" | "YE" | "YT" | "ZA" | "ZM" | "ZW";
/** The 2-letter continent codes Cloudflare uses */
declare type ContinentCode = "AF" | "AN" | "AS" | "EU" | "NA" | "OC" | "SA";
type CfProperties<HostMetadata = unknown> = IncomingRequestCfProperties<HostMetadata> | RequestInitCfProperties;
interface D1Meta {
    duration: number;
    size_after: number;
    rows_read: number;
    rows_written: number;
    last_row_id: number;
    changed_db: boolean;
    changes: number;
    /**
     * The region of the database instance that executed the query.
     */
    served_by_region?: string;
    /**
     * True if-and-only-if the database instance that executed the query was the primary.
     */
    served_by_primary?: boolean;
    timings?: {
        /**
         * The duration of the SQL query execution by the database instance. It doesn't include any network time.
         */
        sql_duration_ms: number;
    };
}
interface D1Response {
    success: true;
    meta: D1Meta & Record<string, unknown>;
    error?: never;
}
type D1Result<T = unknown> = D1Response & {
    results: T[];
};
interface D1ExecResult {
    count: number;
    duration: number;
}
type D1SessionConstraint = 
// Indicates that the first query should go to the primary, and the rest queries
// using the same D1DatabaseSession will go to any replica that is consistent with
// the bookmark maintained by the session (returned by the first query).
"first-primary"
// Indicates that the first query can go anywhere (primary or replica), and the rest queries
// using the same D1DatabaseSession will go to any replica that is consistent with
// the bookmark maintained by the session (returned by the first query).
 | "first-unconstrained";
type D1SessionBookmark = string;
declare abstract class D1Database {
    prepare(query: string): D1PreparedStatement;
    batch<T = unknown>(statements: D1PreparedStatement[]): Promise<D1Result<T>[]>;
    exec(query: string): Promise<D1ExecResult>;
    /**
     * Creates a new D1 Session anchored at the given constraint or the bookmark.
     * All queries executed using the created session will have sequential consistency,
     * meaning that all writes done through the session will be visible in subsequent reads.
     *
     * @param constraintOrBookmark Either the session constraint or the explicit bookmark to anchor the created session.
     */
    withSession(constraintOrBookmark?: D1SessionBookmark | D1SessionConstraint): D1DatabaseSession;
    /**
     * @deprecated dump() will be removed soon, only applies to deprecated alpha v1 databases.
     */
    dump(): Promise<ArrayBuffer>;
}
declare abstract class D1DatabaseSession {
    prepare(query: string): D1PreparedStatement;
    batch<T = unknown>(statements: D1PreparedStatement[]): Promise<D1Result<T>[]>;
    /**
     * @returns The latest session bookmark across all executed queries on the session.
     *          If no query has been executed yet, `null` is returned.
     */
    getBookmark(): D1SessionBookmark | null;
}
declare abstract class D1PreparedStatement {
    bind(...values: unknown[]): D1PreparedStatement;
    first<T = unknown>(colName: string): Promise<T | null>;
    first<T = Record<string, unknown>>(): Promise<T | null>;
    run<T = Record<string, unknown>>(): Promise<D1Result<T>>;
    all<T = Record<string, unknown>>(): Promise<D1Result<T>>;
    raw<T = unknown[]>(options: {
        columnNames: true;
    }): Promise<[
        string[],
        ...T[]
    ]>;
    raw<T = unknown[]>(options?: {
        columnNames?: false;
    }): Promise<T[]>;
}
// `Disposable` was added to TypeScript's standard lib types in version 5.2.
// To support older TypeScript versions, define an empty `Disposable` interface.
// Users won't be able to use `using`/`Symbol.dispose` without upgrading to 5.2,
// but this will ensure type checking on older versions still passes.
// TypeScript's interface merging will ensure our empty interface is effectively
// ignored when `Disposable` is included in the standard lib.
interface Disposable {
}
/**
 * An email message that can be sent from a Worker.
 */
interface EmailMessage {
    /**
     * Envelope From attribute of the email message.
     */
    readonly from: string;
    /**
     * Envelope To attribute of the email message.
     */
    readonly to: string;
}
/**
 * An email message that is sent to a consumer Worker and can be rejected/forwarded.
 */
interface ForwardableEmailMessage extends EmailMessage {
    /**
     * Stream of the email message content.
     */
    readonly raw: ReadableStream<Uint8Array>;
    /**
     * An [Headers object](https://developer.mozilla.org/en-US/docs/Web/API/Headers).
     */
    readonly headers: Headers;
    /**
     * Size of the email message content.
     */
    readonly rawSize: number;
    /**
     * Reject this email message by returning a permanent SMTP error back to the connecting client including the given reason.
     * @param reason The reject reason.
     * @returns void
     */
    setReject(reason: string): void;
    /**
     * Forward this email message to a verified destination address of the account.
     * @param rcptTo Verified destination address.
     * @param headers A [Headers object](https://developer.mozilla.org/en-US/docs/Web/API/Headers).
     * @returns A promise that resolves when the email message is forwarded.
     */
    forward(rcptTo: string, headers?: Headers): Promise<void>;
    /**
     * Reply to the sender of this email message with a new EmailMessage object.
     * @param message The reply message.
     * @returns A promise that resolves when the email message is replied.
     */
    reply(message: EmailMessage): Promise<void>;
}
/**
 * A binding that allows a Worker to send email messages.
 */
interface SendEmail {
    send(message: EmailMessage): Promise<void>;
}
declare abstract class EmailEvent extends ExtendableEvent {
    readonly message: ForwardableEmailMessage;
}
declare type EmailExportedHandler<Env = unknown> = (message: ForwardableEmailMessage, env: Env, ctx: ExecutionContext) => void | Promise<void>;
declare module "cloudflare:email" {
    let _EmailMessage: {
        prototype: EmailMessage;
        new (from: string, to: string, raw: ReadableStream | string): EmailMessage;
    };
    export { _EmailMessage as EmailMessage };
}
/**
 * Hello World binding to serve as an explanatory example. DO NOT USE
 */
interface HelloWorldBinding {
    /**
     * Retrieve the current stored value
     */
    get(): Promise<{
        value: string;
        ms?: number;
    }>;
    /**
     * Set a new stored value
     */
    set(value: string): Promise<void>;
}
interface Hyperdrive {
    /**
     * Connect directly to Hyperdrive as if it's your database, returning a TCP socket.
     *
     * Calling this method returns an idential socket to if you call
     * `connect("host:port")` using the `host` and `port` fields from this object.
     * Pick whichever approach works better with your preferred DB client library.
     *
     * Note that this socket is not yet authenticated -- it's expected that your
     * code (or preferably, the client library of your choice) will authenticate
     * using the information in this class's readonly fields.
     */
    connect(): Socket;
    /**
     * A valid DB connection string that can be passed straight into the typical
     * client library/driver/ORM. This will typically be the easiest way to use
     * Hyperdrive.
     */
    readonly connectionString: string;
    /*
     * A randomly generated hostname that is only valid within the context of the
     * currently running Worker which, when passed into `connect()` function from
     * the "cloudflare:sockets" module, will connect to the Hyperdrive instance
     * for your database.
     */
    readonly host: string;
    /*
     * The port that must be paired the the host field when connecting.
     */
    readonly port: number;
    /*
     * The username to use when authenticating to your database via Hyperdrive.
     * Unlike the host and password, this will be the same every time
     */
    readonly user: string;
    /*
     * The randomly generated password to use when authenticating to your
     * database via Hyperdrive. Like the host field, this password is only valid
     * within the context of the currently running Worker instance from which
     * it's read.
     */
    readonly password: string;
    /*
     * The name of the database to connect to.
     */
    readonly database: string;
}
// Copyright (c) 2024 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0
type ImageInfoResponse = {
    format: 'image/svg+xml';
} | {
    format: string;
    fileSize: number;
    width: number;
    height: number;
};
type ImageTransform = {
    width?: number;
    height?: number;
    background?: string;
    blur?: number;
    border?: {
        color?: string;
        width?: number;
    } | {
        top?: number;
        bottom?: number;
        left?: number;
        right?: number;
    };
    brightness?: number;
    contrast?: number;
    fit?: 'scale-down' | 'contain' | 'pad' | 'squeeze' | 'cover' | 'crop';
    flip?: 'h' | 'v' | 'hv';
    gamma?: number;
    gravity?: 'left' | 'right' | 'top' | 'bottom' | 'center' | 'auto' | 'entropy' | {
        x?: number;
        y?: number;
        mode: 'remainder' | 'box-center';
    };
    rotate?: 0 | 90 | 180 | 270;
    saturation?: number;
    sharpen?: number;
    trim?: "border" | {
        top?: number;
        bottom?: number;
        left?: number;
        right?: number;
        width?: number;
        height?: number;
        border?: boolean | {
            color?: string;
            tolerance?: number;
            keep?: number;
        };
    };
};
type ImageDrawOptions = {
    opacity?: number;
    repeat?: boolean | string;
    top?: number;
    left?: number;
    bottom?: number;
    right?: number;
};
type ImageOutputOptions = {
    format: 'image/jpeg' | 'image/png' | 'image/gif' | 'image/webp' | 'image/avif' | 'rgb' | 'rgba';
    quality?: number;
    background?: string;
};
interface ImagesBinding {
    /**
     * Get image metadata (type, width and height)
     * @throws {@link ImagesError} with code 9412 if input is not an image
     * @param stream The image bytes
     */
    info(stream: ReadableStream<Uint8Array>): Promise<ImageInfoResponse>;
    /**
     * Begin applying a series of transformations to an image
     * @param stream The image bytes
     * @returns A transform handle
     */
    input(stream: ReadableStream<Uint8Array>): ImageTransformer;
}
interface ImageTransformer {
    /**
     * Apply transform next, returning a transform handle.
     * You can then apply more transformations, draw, or retrieve the output.
     * @param transform
     */
    transform(transform: ImageTransform): ImageTransformer;
    /**
     * Draw an image on this transformer, returning a transform handle.
     * You can then apply more transformations, draw, or retrieve the output.
     * @param image The image (or transformer that will give the image) to draw
     * @param options The options configuring how to draw the image
     */
    draw(image: ReadableStream<Uint8Array> | ImageTransformer, options?: ImageDrawOptions): ImageTransformer;
    /**
     * Retrieve the image that results from applying the transforms to the
     * provided input
     * @param options Options that apply to the output e.g. output format
     */
    output(options: ImageOutputOptions): Promise<ImageTransformationResult>;
}
interface ImageTransformationResult {
    /**
     * The image as a response, ready to store in cache or return to users
     */
    response(): Response;
    /**
     * The content type of the returned image
     */
    contentType(): string;
    /**
     * The bytes of the response
     */
    image(): ReadableStream<Uint8Array>;
}
interface ImagesError extends Error {
    readonly code: number;
    readonly message: string;
    readonly stack?: string;
}
type Params<P extends string = any> = Record<P, string | string[]>;
type EventContext<Env, P extends string, Data> = {
    request: Request<unknown, IncomingRequestCfProperties<unknown>>;
    functionPath: string;
    waitUntil: (promise: Promise<any>) => void;
    passThroughOnException: () => void;
    next: (input?: Request | string, init?: RequestInit) => Promise<Response>;
    env: Env & {
        ASSETS: {
            fetch: typeof fetch;
        };
    };
    params: Params<P>;
    data: Data;
};
type PagesFunction<Env = unknown, Params extends string = any, Data extends Record<string, unknown> = Record<string, unknown>> = (context: EventContext<Env, Params, Data>) => Response | Promise<Response>;
type EventPluginContext<Env, P extends string, Data, PluginArgs> = {
    request: Request<unknown, IncomingRequestCfProperties<unknown>>;
    functionPath: string;
    waitUntil: (promise: Promise<any>) => void;
    passThroughOnException: () => void;
    next: (input?: Request | string, init?: RequestInit) => Promise<Response>;
    env: Env & {
        ASSETS: {
            fetch: typeof fetch;
        };
    };
    params: Params<P>;
    data: Data;
    pluginArgs: PluginArgs;
};
type PagesPluginFunction<Env = unknown, Params extends string = any, Data extends Record<string, unknown> = Record<string, unknown>, PluginArgs = unknown> = (context: EventPluginContext<Env, Params, Data, PluginArgs>) => Response | Promise<Response>;
declare module "assets:*" {
    export const onRequest: PagesFunction;
}
// Copyright (c) 2022-2023 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0
declare module "cloudflare:pipelines" {
    export abstract class PipelineTransformationEntrypoint<Env = unknown, I extends PipelineRecord = PipelineRecord, O extends PipelineRecord = PipelineRecord> {
        protected env: Env;
        protected ctx: ExecutionContext;
        constructor(ctx: ExecutionContext, env: Env);
        /**
         * run recieves an array of PipelineRecord which can be
         * transformed and returned to the pipeline
         * @param records Incoming records from the pipeline to be transformed
         * @param metadata Information about the specific pipeline calling the transformation entrypoint
         * @returns A promise containing the transformed PipelineRecord array
         */
        public run(records: I[], metadata: PipelineBatchMetadata): Promise<O[]>;
    }
    export type PipelineRecord = Record<string, unknown>;
    export type PipelineBatchMetadata = {
        pipelineId: string;
        pipelineName: string;
    };
    export interface Pipeline<T extends PipelineRecord = PipelineRecord> {
        /**
         * The Pipeline interface represents the type of a binding to a Pipeline
         *
         * @param records The records to send to the pipeline
         */
        send(records: T[]): Promise<void>;
    }
}
// PubSubMessage represents an incoming PubSub message.
// The message includes metadata about the broker, the client, and the payload
// itself.
// https://developers.cloudflare.com/pub-sub/
interface PubSubMessage {
    // Message ID
    readonly mid: number;
    // MQTT broker FQDN in the form mqtts://BROKER.NAMESPACE.cloudflarepubsub.com:PORT
    readonly broker: string;
    // The MQTT topic the message was sent on.
    readonly topic: string;
    // The client ID of the client that published this message.
    readonly clientId: string;
    // The unique identifier (JWT ID) used by the client to authenticate, if token
    // auth was used.
    readonly jti?: string;
    // A Unix timestamp (seconds from Jan 1, 1970), set when the Pub/Sub Broker
    // received the message from the client.
    readonly receivedAt: number;
    // An (optional) string with the MIME type of the payload, if set by the
    // client.
    readonly contentType: string;
    // Set to 1 when the payload is a UTF-8 string
    // https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901063
    readonly payloadFormatIndicator: number;
    // Pub/Sub (MQTT) payloads can be UTF-8 strings, or byte arrays.
    // You can use payloadFormatIndicator to inspect this before decoding.
    payload: string | Uint8Array;
}
// JsonWebKey extended by kid parameter
interface JsonWebKeyWithKid extends JsonWebKey {
    // Key Identifier of the JWK
    readonly kid: string;
}
interface RateLimitOptions {
    key: string;
}
interface RateLimitOutcome {
    success: boolean;
}
interface RateLimit {
    /**
     * Rate limit a request based on the provided options.
     * @see https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/
     * @returns A promise that resolves with the outcome of the rate limit.
     */
    limit(options: RateLimitOptions): Promise<RateLimitOutcome>;
}
// Namespace for RPC utility types. Unfortunately, we can't use a `module` here as these types need
// to referenced by `Fetcher`. This is included in the "importable" version of the types which
// strips all `module` blocks.
declare namespace Rpc {
    // Branded types for identifying `WorkerEntrypoint`/`DurableObject`/`Target`s.
    // TypeScript uses *structural* typing meaning anything with the same shape as type `T` is a `T`.
    // For the classes exported by `cloudflare:workers` we want *nominal* typing (i.e. we only want to
    // accept `WorkerEntrypoint` from `cloudflare:workers`, not any other class with the same shape)
    export const __RPC_STUB_BRAND: '__RPC_STUB_BRAND';
    export const __RPC_TARGET_BRAND: '__RPC_TARGET_BRAND';
    export const __WORKER_ENTRYPOINT_BRAND: '__WORKER_ENTRYPOINT_BRAND';
    export const __DURABLE_OBJECT_BRAND: '__DURABLE_OBJECT_BRAND';
    export const __WORKFLOW_ENTRYPOINT_BRAND: '__WORKFLOW_ENTRYPOINT_BRAND';
    export interface RpcTargetBranded {
        [__RPC_TARGET_BRAND]: never;
    }
    export interface WorkerEntrypointBranded {
        [__WORKER_ENTRYPOINT_BRAND]: never;
    }
    export interface DurableObjectBranded {
        [__DURABLE_OBJECT_BRAND]: never;
    }
    export interface WorkflowEntrypointBranded {
        [__WORKFLOW_ENTRYPOINT_BRAND]: never;
    }
    export type EntrypointBranded = WorkerEntrypointBranded | DurableObjectBranded | WorkflowEntrypointBranded;
    // Types that can be used through `Stub`s
    export type Stubable = RpcTargetBranded | ((...args: any[]) => any);
    // Types that can be passed over RPC
    // The reason for using a generic type here is to build a serializable subset of structured
    //   cloneable composite types. This allows types defined with the "interface" keyword to pass the
    //   serializable check as well. Otherwise, only types defined with the "type" keyword would pass.
    type Serializable<T> = 
    // Structured cloneables
    BaseType
    // Structured cloneable composites
     | Map<T extends Map<infer U, unknown> ? Serializable<U> : never, T extends Map<unknown, infer U> ? Serializable<U> : never> | Set<T extends Set<infer U> ? Serializable<U> : never> | ReadonlyArray<T extends ReadonlyArray<infer U> ? Serializable<U> : never> | {
        [K in keyof T]: K extends number | string ? Serializable<T[K]> : never;
    }
    // Special types
     | Stub<Stubable>
    // Serialized as stubs, see `Stubify`
     | Stubable;
    // Base type for all RPC stubs, including common memory management methods.
    // `T` is used as a marker type for unwrapping `Stub`s later.
    interface StubBase<T extends Stubable> extends Disposable {
        [__RPC_STUB_BRAND]: T;
        dup(): this;
    }
    export type Stub<T extends Stubable> = Provider<T> & StubBase<T>;
    // This represents all the types that can be sent as-is over an RPC boundary
    type BaseType = void | undefined | null | boolean | number | bigint | string | TypedArray | ArrayBuffer | DataView | Date | Error | RegExp | ReadableStream<Uint8Array> | WritableStream<Uint8Array> | Request | Response | Headers;
    // Recursively rewrite all `Stubable` types with `Stub`s
    // prettier-ignore
    type Stubify<T> = T extends Stubable ? Stub<T> : T extends Map<infer K, infer V> ? Map<Stubify<K>, Stubify<V>> : T extends Set<infer V> ? Set<Stubify<V>> : T extends Array<infer V> ? Array<Stubify<V>> : T extends ReadonlyArray<infer V> ? ReadonlyArray<Stubify<V>> : T extends BaseType ? T : T extends {
        [key: string | number]: any;
    } ? {
        [K in keyof T]: Stubify<T[K]>;
    } : T;
    // Recursively rewrite all `Stub<T>`s with the corresponding `T`s.
    // Note we use `StubBase` instead of `Stub` here to avoid circular dependencies:
    // `Stub` depends on `Provider`, which depends on `Unstubify`, which would depend on `Stub`.
    // prettier-ignore
    type Unstubify<T> = T extends StubBase<infer V> ? V : T extends Map<infer K, infer V> ? Map<Unstubify<K>, Unstubify<V>> : T extends Set<infer V> ? Set<Unstubify<V>> : T extends Array<infer V> ? Array<Unstubify<V>> : T extends ReadonlyArray<infer V> ? ReadonlyArray<Unstubify<V>> : T extends BaseType ? T : T extends {
        [key: string | number]: unknown;
    } ? {
        [K in keyof T]: Unstubify<T[K]>;
    } : T;
    type UnstubifyAll<A extends any[]> = {
        [I in keyof A]: Unstubify<A[I]>;
    };
    // Utility type for adding `Provider`/`Disposable`s to `object` types only.
    // Note `unknown & T` is equivalent to `T`.
    type MaybeProvider<T> = T extends object ? Provider<T> : unknown;
    type MaybeDisposable<T> = T extends object ? Disposable : unknown;
    // Type for method return or property on an RPC interface.
    // - Stubable types are replaced by stubs.
    // - Serializable types are passed by value, with stubable types replaced by stubs
    //   and a top-level `Disposer`.
    // Everything else can't be passed over PRC.
    // Technically, we use custom thenables here, but they quack like `Promise`s.
    // Intersecting with `(Maybe)Provider` allows pipelining.
    // prettier-ignore
    type Result<R> = R extends Stubable ? Promise<Stub<R>> & Provider<R> : R extends Serializable<R> ? Promise<Stubify<R> & MaybeDisposable<R>> & MaybeProvider<R> : never;
    // Type for method or property on an RPC interface.
    // For methods, unwrap `Stub`s in parameters, and rewrite returns to be `Result`s.
    // Unwrapping `Stub`s allows calling with `Stubable` arguments.
    // For properties, rewrite types to be `Result`s.
    // In each case, unwrap `Promise`s.
    type MethodOrProperty<V> = V extends (...args: infer P) => infer R ? (...args: UnstubifyAll<P>) => Result<Awaited<R>> : Result<Awaited<V>>;
    // Type for the callable part of an `Provider` if `T` is callable.
    // This is intersected with methods/properties.
    type MaybeCallableProvider<T> = T extends (...args: any[]) => any ? MethodOrProperty<T> : unknown;
    // Base type for all other types providing RPC-like interfaces.
    // Rewrites all methods/properties to be `MethodOrProperty`s, while preserving callable types.
    // `Reserved` names (e.g. stub method names like `dup()`) and symbols can't be accessed over RPC.
    export type Provider<T extends object, Reserved extends string = never> = MaybeCallableProvider<T> & {
        [K in Exclude<keyof T, Reserved | symbol | keyof StubBase<never>>]: MethodOrProperty<T[K]>;
    };
}
declare namespace Cloudflare {
    interface Env {
    }
}
declare module 'cloudflare:workers' {
    export type RpcStub<T extends Rpc.Stubable> = Rpc.Stub<T>;
    export const RpcStub: {
        new <T extends Rpc.Stubable>(value: T): Rpc.Stub<T>;
    };
    export abstract class RpcTarget implements Rpc.RpcTargetBranded {
        [Rpc.__RPC_TARGET_BRAND]: never;
    }
    // `protected` fields don't appear in `keyof`s, so can't be accessed over RPC
    export abstract class WorkerEntrypoint<Env = unknown> implements Rpc.WorkerEntrypointBranded {
        [Rpc.__WORKER_ENTRYPOINT_BRAND]: never;
        protected ctx: ExecutionContext;
        protected env: Env;
        constructor(ctx: ExecutionContext, env: Env);
        fetch?(request: Request): Response | Promise<Response>;
        tail?(events: TraceItem[]): void | Promise<void>;
        trace?(traces: TraceItem[]): void | Promise<void>;
        scheduled?(controller: ScheduledController): void | Promise<void>;
        queue?(batch: MessageBatch<unknown>): void | Promise<void>;
        test?(controller: TestController): void | Promise<void>;
    }
    export abstract class DurableObject<Env = unknown> implements Rpc.DurableObjectBranded {
        [Rpc.__DURABLE_OBJECT_BRAND]: never;
        protected ctx: DurableObjectState;
        protected env: Env;
        constructor(ctx: DurableObjectState, env: Env);
        fetch?(request: Request): Response | Promise<Response>;
        alarm?(alarmInfo?: AlarmInvocationInfo): void | Promise<void>;
        webSocketMessage?(ws: WebSocket, message: string | ArrayBuffer): void | Promise<void>;
        webSocketClose?(ws: WebSocket, code: number, reason: string, wasClean: boolean): void | Promise<void>;
        webSocketError?(ws: WebSocket, error: unknown): void | Promise<void>;
    }
    export type WorkflowDurationLabel = 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';
    export type WorkflowSleepDuration = `${number} ${WorkflowDurationLabel}${'s' | ''}` | number;
    export type WorkflowDelayDuration = WorkflowSleepDuration;
    export type WorkflowTimeoutDuration = WorkflowSleepDuration;
    export type WorkflowRetentionDuration = WorkflowSleepDuration;
    export type WorkflowBackoff = 'constant' | 'linear' | 'exponential';
    export type WorkflowStepConfig = {
        retries?: {
            limit: number;
            delay: WorkflowDelayDuration | number;
            backoff?: WorkflowBackoff;
        };
        timeout?: WorkflowTimeoutDuration | number;
    };
    export type WorkflowEvent<T> = {
        payload: Readonly<T>;
        timestamp: Date;
        instanceId: string;
    };
    export type WorkflowStepEvent<T> = {
        payload: Readonly<T>;
        timestamp: Date;
        type: string;
    };
    export abstract class WorkflowStep {
        do<T extends Rpc.Serializable<T>>(name: string, callback: () => Promise<T>): Promise<T>;
        do<T extends Rpc.Serializable<T>>(name: string, config: WorkflowStepConfig, callback: () => Promise<T>): Promise<T>;
        sleep: (name: string, duration: WorkflowSleepDuration) => Promise<void>;
        sleepUntil: (name: string, timestamp: Date | number) => Promise<void>;
        waitForEvent<T extends Rpc.Serializable<T>>(name: string, options: {
            type: string;
            timeout?: WorkflowTimeoutDuration | number;
        }): Promise<WorkflowStepEvent<T>>;
    }
    export abstract class WorkflowEntrypoint<Env = unknown, T extends Rpc.Serializable<T> | unknown = unknown> implements Rpc.WorkflowEntrypointBranded {
        [Rpc.__WORKFLOW_ENTRYPOINT_BRAND]: never;
        protected ctx: ExecutionContext;
        protected env: Env;
        constructor(ctx: ExecutionContext, env: Env);
        run(event: Readonly<WorkflowEvent<T>>, step: WorkflowStep): Promise<unknown>;
    }
    export const env: Cloudflare.Env;
}
interface SecretsStoreSecret {
    /**
     * Get a secret from the Secrets Store, returning a string of the secret value
     * if it exists, or throws an error if it does not exist
     */
    get(): Promise<string>;
}
declare module "cloudflare:sockets" {
    function _connect(address: string | SocketAddress, options?: SocketOptions): Socket;
    export { _connect as connect };
}
declare namespace TailStream {
    interface Header {
        readonly name: string;
        readonly value: string;
    }
    interface FetchEventInfo {
        readonly type: "fetch";
        readonly method: string;
        readonly url: string;
        readonly cfJson: string;
        readonly headers: Header[];
    }
    interface JsRpcEventInfo {
        readonly type: "jsrpc";
        readonly methodName: string;
    }
    interface ScheduledEventInfo {
        readonly type: "scheduled";
        readonly scheduledTime: Date;
        readonly cron: string;
    }
    interface AlarmEventInfo {
        readonly type: "alarm";
        readonly scheduledTime: Date;
    }
    interface QueueEventInfo {
        readonly type: "queue";
        readonly queueName: string;
        readonly batchSize: number;
    }
    interface EmailEventInfo {
        readonly type: "email";
        readonly mailFrom: string;
        readonly rcptTo: string;
        readonly rawSize: number;
    }
    interface TraceEventInfo {
        readonly type: "trace";
        readonly traces: (string | null)[];
    }
    interface HibernatableWebSocketEventInfoMessage {
        readonly type: "message";
    }
    interface HibernatableWebSocketEventInfoError {
        readonly type: "error";
    }
    interface HibernatableWebSocketEventInfoClose {
        readonly type: "close";
        readonly code: number;
        readonly wasClean: boolean;
    }
    interface HibernatableWebSocketEventInfo {
        readonly type: "hibernatableWebSocket";
        readonly info: HibernatableWebSocketEventInfoClose | HibernatableWebSocketEventInfoError | HibernatableWebSocketEventInfoMessage;
    }
    interface Resume {
        readonly type: "resume";
        readonly attachment?: any;
    }
    interface CustomEventInfo {
        readonly type: "custom";
    }
    interface FetchResponseInfo {
        readonly type: "fetch";
        readonly statusCode: number;
    }
    type EventOutcome = "ok" | "canceled" | "exception" | "unknown" | "killSwitch" | "daemonDown" | "exceededCpu" | "exceededMemory" | "loadShed" | "responseStreamDisconnected" | "scriptNotFound";
    interface ScriptVersion {
        readonly id: string;
        readonly tag?: string;
        readonly message?: string;
    }
    interface Trigger {
        readonly traceId: string;
        readonly invocationId: string;
        readonly spanId: string;
    }
    interface Onset {
        readonly type: "onset";
        readonly dispatchNamespace?: string;
        readonly entrypoint?: string;
        readonly executionModel: string;
        readonly scriptName?: string;
        readonly scriptTags?: string[];
        readonly scriptVersion?: ScriptVersion;
        readonly trigger?: Trigger;
        readonly info: FetchEventInfo | JsRpcEventInfo | ScheduledEventInfo | AlarmEventInfo | QueueEventInfo | EmailEventInfo | TraceEventInfo | HibernatableWebSocketEventInfo | Resume | CustomEventInfo;
    }
    interface Outcome {
        readonly type: "outcome";
        readonly outcome: EventOutcome;
        readonly cpuTime: number;
        readonly wallTime: number;
    }
    interface Hibernate {
        readonly type: "hibernate";
    }
    interface SpanOpen {
        readonly type: "spanOpen";
        readonly name: string;
        readonly info?: FetchEventInfo | JsRpcEventInfo | Attributes;
    }
    interface SpanClose {
        readonly type: "spanClose";
        readonly outcome: EventOutcome;
    }
    interface DiagnosticChannelEvent {
        readonly type: "diagnosticChannel";
        readonly channel: string;
        readonly message: any;
    }
    interface Exception {
        readonly type: "exception";
        readonly name: string;
        readonly message: string;
        readonly stack?: string;
    }
    interface Log {
        readonly type: "log";
        readonly level: "debug" | "error" | "info" | "log" | "warn";
        readonly message: string;
    }
    interface Return {
        readonly type: "return";
        readonly info?: FetchResponseInfo;
    }
    interface Link {
        readonly type: "link";
        readonly label?: string;
        readonly traceId: string;
        readonly invocationId: string;
        readonly spanId: string;
    }
    interface Attribute {
        readonly name: string;
        readonly value: string | string[] | boolean | boolean[] | number | number[] | bigint | bigint[];
    }
    interface Attributes {
        readonly type: "attributes";
        readonly info: Attribute[];
    }
    type EventType = Onset | Outcome | Hibernate | SpanOpen | SpanClose | DiagnosticChannelEvent | Exception | Log | Return | Link | Attributes;
    interface TailEvent<Event extends EventType> {
        readonly invocationId: string;
        readonly spanId: string;
        readonly timestamp: Date;
        readonly sequence: number;
        readonly event: Event;
    }
    type TailEventHandler<Event extends EventType = EventType> = (event: TailEvent<Event>) => void | Promise<void>;
    type TailEventHandlerObject = {
        outcome?: TailEventHandler<Outcome>;
        hibernate?: TailEventHandler<Hibernate>;
        spanOpen?: TailEventHandler<SpanOpen>;
        spanClose?: TailEventHandler<SpanClose>;
        diagnosticChannel?: TailEventHandler<DiagnosticChannelEvent>;
        exception?: TailEventHandler<Exception>;
        log?: TailEventHandler<Log>;
        return?: TailEventHandler<Return>;
        link?: TailEventHandler<Link>;
        attributes?: TailEventHandler<Attributes>;
    };
    type TailEventHandlerType = TailEventHandler | TailEventHandlerObject;
}
// Copyright (c) 2022-2023 Cloudflare, Inc.
// Licensed under the Apache 2.0 license found in the LICENSE file or at:
//     https://opensource.org/licenses/Apache-2.0
/**
 * Data types supported for holding vector metadata.
 */
type VectorizeVectorMetadataValue = string | number | boolean | string[];
/**
 * Additional information to associate with a vector.
 */
type VectorizeVectorMetadata = VectorizeVectorMetadataValue | Record<string, VectorizeVectorMetadataValue>;
type VectorFloatArray = Float32Array | Float64Array;
interface VectorizeError {
    code?: number;
    error: string;
}
/**
 * Comparison logic/operation to use for metadata filtering.
 *
 * This list is expected to grow as support for more operations are released.
 */
type VectorizeVectorMetadataFilterOp = "$eq" | "$ne";
/**
 * Filter criteria for vector metadata used to limit the retrieved query result set.
 */
type VectorizeVectorMetadataFilter = {
    [field: string]: Exclude<VectorizeVectorMetadataValue, string[]> | null | {
        [Op in VectorizeVectorMetadataFilterOp]?: Exclude<VectorizeVectorMetadataValue, string[]> | null;
    };
};
/**
 * Supported distance metrics for an index.
 * Distance metrics determine how other "similar" vectors are determined.
 */
type VectorizeDistanceMetric = "euclidean" | "cosine" | "dot-product";
/**
 * Metadata return levels for a Vectorize query.
 *
 * Default to "none".
 *
 * @property all      Full metadata for the vector return set, including all fields (including those un-indexed) without truncation. This is a more expensive retrieval, as it requires additional fetching & reading of un-indexed data.
 * @property indexed  Return all metadata fields configured for indexing in the vector return set. This level of retrieval is "free" in that no additional overhead is incurred returning this data. However, note that indexed metadata is subject to truncation (especially for larger strings).
 * @property none     No indexed metadata will be returned.
 */
type VectorizeMetadataRetrievalLevel = "all" | "indexed" | "none";
interface VectorizeQueryOptions {
    topK?: number;
    namespace?: string;
    returnValues?: boolean;
    returnMetadata?: boolean | VectorizeMetadataRetrievalLevel;
    filter?: VectorizeVectorMetadataFilter;
}
/**
 * Information about the configuration of an index.
 */
type VectorizeIndexConfig = {
    dimensions: number;
    metric: VectorizeDistanceMetric;
} | {
    preset: string; // keep this generic, as we'll be adding more presets in the future and this is only in a read capacity
};
/**
 * Metadata about an existing index.
 *
 * This type is exclusively for the Vectorize **beta** and will be deprecated once Vectorize RC is released.
 * See {@link VectorizeIndexInfo} for its post-beta equivalent.
 */
interface VectorizeIndexDetails {
    /** The unique ID of the index */
    readonly id: string;
    /** The name of the index. */
    name: string;
    /** (optional) A human readable description for the index. */
    description?: string;
    /** The index configuration, including the dimension size and distance metric. */
    config: VectorizeIndexConfig;
    /** The number of records containing vectors within the index. */
    vectorsCount: number;
}
/**
 * Metadata about an existing index.
 */
interface VectorizeIndexInfo {
    /** The number of records containing vectors within the index. */
    vectorCount: number;
    /** Number of dimensions the index has been configured for. */
    dimensions: number;
    /** ISO 8601 datetime of the last processed mutation on in the index. All changes before this mutation will be reflected in the index state. */
    processedUpToDatetime: number;
    /** UUIDv4 of the last mutation processed by the index. All changes before this mutation will be reflected in the index state. */
    processedUpToMutation: number;
}
/**
 * Represents a single vector value set along with its associated metadata.
 */
interface VectorizeVector {
    /** The ID for the vector. This can be user-defined, and must be unique. It should uniquely identify the object, and is best set based on the ID of what the vector represents. */
    id: string;
    /** The vector values */
    values: VectorFloatArray | number[];
    /** The namespace this vector belongs to. */
    namespace?: string;
    /** Metadata associated with the vector. Includes the values of other fields and potentially additional details. */
    metadata?: Record<string, VectorizeVectorMetadata>;
}
/**
 * Represents a matched vector for a query along with its score and (if specified) the matching vector information.
 */
type VectorizeMatch = Pick<Partial<VectorizeVector>, "values"> & Omit<VectorizeVector, "values"> & {
    /** The score or rank for similarity, when returned as a result */
    score: number;
};
/**
 * A set of matching {@link VectorizeMatch} for a particular query.
 */
interface VectorizeMatches {
    matches: VectorizeMatch[];
    count: number;
}
/**
 * Results of an operation that performed a mutation on a set of vectors.
 * Here, `ids` is a list of vectors that were successfully processed.
 *
 * This type is exclusively for the Vectorize **beta** and will be deprecated once Vectorize RC is released.
 * See {@link VectorizeAsyncMutation} for its post-beta equivalent.
 */
interface VectorizeVectorMutation {
    /* List of ids of vectors that were successfully processed. */
    ids: string[];
    /* Total count of the number of processed vectors. */
    count: number;
}
/**
 * Result type indicating a mutation on the Vectorize Index.
 * Actual mutations are processed async where the `mutationId` is the unique identifier for the operation.
 */
interface VectorizeAsyncMutation {
    /** The unique identifier for the async mutation operation containing the changeset. */
    mutationId: string;
}
/**
 * A Vectorize Vector Search Index for querying vectors/embeddings.
 *
 * This type is exclusively for the Vectorize **beta** and will be deprecated once Vectorize RC is released.
 * See {@link Vectorize} for its new implementation.
 */
declare abstract class VectorizeIndex {
    /**
     * Get information about the currently bound index.
     * @returns A promise that resolves with information about the current index.
     */
    public describe(): Promise<VectorizeIndexDetails>;
    /**
     * Use the provided vector to perform a similarity search across the index.
     * @param vector Input vector that will be used to drive the similarity search.
     * @param options Configuration options to massage the returned data.
     * @returns A promise that resolves with matched and scored vectors.
     */
    public query(vector: VectorFloatArray | number[], options?: VectorizeQueryOptions): Promise<VectorizeMatches>;
    /**
     * Insert a list of vectors into the index dataset. If a provided id exists, an error will be thrown.
     * @param vectors List of vectors that will be inserted.
     * @returns A promise that resolves with the ids & count of records that were successfully processed.
     */
    public insert(vectors: VectorizeVector[]): Promise<VectorizeVectorMutation>;
    /**
     * Upsert a list of vectors into the index dataset. If a provided id exists, it will be replaced with the new values.
     * @param vectors List of vectors that will be upserted.
     * @returns A promise that resolves with the ids & count of records that were successfully processed.
     */
    public upsert(vectors: VectorizeVector[]): Promise<VectorizeVectorMutation>;
    /**
     * Delete a list of vectors with a matching id.
     * @param ids List of vector ids that should be deleted.
     * @returns A promise that resolves with the ids & count of records that were successfully processed (and thus deleted).
     */
    public deleteByIds(ids: string[]): Promise<VectorizeVectorMutation>;
    /**
     * Get a list of vectors with a matching id.
     * @param ids List of vector ids that should be returned.
     * @returns A promise that resolves with the raw unscored vectors matching the id set.
     */
    public getByIds(ids: string[]): Promise<VectorizeVector[]>;
}
/**
 * A Vectorize Vector Search Index for querying vectors/embeddings.
 *
 * Mutations in this version are async, returning a mutation id.
 */
declare abstract class Vectorize {
    /**
     * Get information about the currently bound index.
     * @returns A promise that resolves with information about the current index.
     */
    public describe(): Promise<VectorizeIndexInfo>;
    /**
     * Use the provided vector to perform a similarity search across the index.
     * @param vector Input vector that will be used to drive the similarity search.
     * @param options Configuration options to massage the returned data.
     * @returns A promise that resolves with matched and scored vectors.
     */
    public query(vector: VectorFloatArray | number[], options?: VectorizeQueryOptions): Promise<VectorizeMatches>;
    /**
     * Use the provided vector-id to perform a similarity search across the index.
     * @param vectorId Id for a vector in the index against which the index should be queried.
     * @param options Configuration options to massage the returned data.
     * @returns A promise that resolves with matched and scored vectors.
     */
    public queryById(vectorId: string, options?: VectorizeQueryOptions): Promise<VectorizeMatches>;
    /**
     * Insert a list of vectors into the index dataset. If a provided id exists, an error will be thrown.
     * @param vectors List of vectors that will be inserted.
     * @returns A promise that resolves with a unique identifier of a mutation containing the insert changeset.
     */
    public insert(vectors: VectorizeVector[]): Promise<VectorizeAsyncMutation>;
    /**
     * Upsert a list of vectors into the index dataset. If a provided id exists, it will be replaced with the new values.
     * @param vectors List of vectors that will be upserted.
     * @returns A promise that resolves with a unique identifier of a mutation containing the upsert changeset.
     */
    public upsert(vectors: VectorizeVector[]): Promise<VectorizeAsyncMutation>;
    /**
     * Delete a list of vectors with a matching id.
     * @param ids List of vector ids that should be deleted.
     * @returns A promise that resolves with a unique identifier of a mutation containing the delete changeset.
     */
    public deleteByIds(ids: string[]): Promise<VectorizeAsyncMutation>;
    /**
     * Get a list of vectors with a matching id.
     * @param ids List of vector ids that should be returned.
     * @returns A promise that resolves with the raw unscored vectors matching the id set.
     */
    public getByIds(ids: string[]): Promise<VectorizeVector[]>;
}
/**
 * The interface for "version_metadata" binding
 * providing metadata about the Worker Version using this binding.
 */
type WorkerVersionMetadata = {
    /** The ID of the Worker Version using this binding */
    id: string;
    /** The tag of the Worker Version using this binding */
    tag: string;
    /** The timestamp of when the Worker Version was uploaded */
    timestamp: string;
};
interface DynamicDispatchLimits {
    /**
     * Limit CPU time in milliseconds.
     */
    cpuMs?: number;
    /**
     * Limit number of subrequests.
     */
    subRequests?: number;
}
interface DynamicDispatchOptions {
    /**
     * Limit resources of invoked Worker script.
     */
    limits?: DynamicDispatchLimits;
    /**
     * Arguments for outbound Worker script, if configured.
     */
    outbound?: {
        [key: string]: any;
    };
}
interface DispatchNamespace {
    /**
    * @param name Name of the Worker script.
    * @param args Arguments to Worker script.
    * @param options Options for Dynamic Dispatch invocation.
    * @returns A Fetcher object that allows you to send requests to the Worker script.
    * @throws If the Worker script does not exist in this dispatch namespace, an error will be thrown.
    */
    get(name: string, args?: {
        [key: string]: any;
    }, options?: DynamicDispatchOptions): Fetcher;
}
declare module 'cloudflare:workflows' {
    /**
     * NonRetryableError allows for a user to throw a fatal error
     * that makes a Workflow instance fail immediately without triggering a retry
     */
    export class NonRetryableError extends Error {
        public constructor(message: string, name?: string);
    }
}
declare abstract class Workflow<PARAMS = unknown> {
    /**
     * Get a handle to an existing instance of the Workflow.
     * @param id Id for the instance of this Workflow
     * @returns A promise that resolves with a handle for the Instance
     */
    public get(id: string): Promise<WorkflowInstance>;
    /**
     * Create a new instance and return a handle to it. If a provided id exists, an error will be thrown.
     * @param options Options when creating an instance including id and params
     * @returns A promise that resolves with a handle for the Instance
     */
    public create(options?: WorkflowInstanceCreateOptions<PARAMS>): Promise<WorkflowInstance>;
    /**
     * Create a batch of instances and return handle for all of them. If a provided id exists, an error will be thrown.
     * `createBatch` is limited at 100 instances at a time or when the RPC limit for the batch (1MiB) is reached.
     * @param batch List of Options when creating an instance including name and params
     * @returns A promise that resolves with a list of handles for the created instances.
     */
    public createBatch(batch: WorkflowInstanceCreateOptions<PARAMS>[]): Promise<WorkflowInstance[]>;
}
type WorkflowDurationLabel = 'second' | 'minute' | 'hour' | 'day' | 'week' | 'month' | 'year';
type WorkflowSleepDuration = `${number} ${WorkflowDurationLabel}${'s' | ''}` | number;
type WorkflowRetentionDuration = WorkflowSleepDuration;
interface WorkflowInstanceCreateOptions<PARAMS = unknown> {
    /**
     * An id for your Workflow instance. Must be unique within the Workflow.
     */
    id?: string;
    /**
     * The event payload the Workflow instance is triggered with
     */
    params?: PARAMS;
    /**
     * The retention policy for Workflow instance.
     * Defaults to the maximum retention period available for the owner's account.
     */
    retention?: {
        successRetention?: WorkflowRetentionDuration;
        errorRetention?: WorkflowRetentionDuration;
    };
}
type InstanceStatus = {
    status: 'queued' // means that instance is waiting to be started (see concurrency limits)
     | 'running' | 'paused' | 'errored' | 'terminated' // user terminated the instance while it was running
     | 'complete' | 'waiting' // instance is hibernating and waiting for sleep or event to finish
     | 'waitingForPause' // instance is finishing the current work to pause
     | 'unknown';
    error?: string;
    output?: object;
};
interface WorkflowError {
    code?: number;
    message: string;
}
declare abstract class WorkflowInstance {
    public id: string;
    /**
     * Pause the instance.
     */
    public pause(): Promise<void>;
    /**
     * Resume the instance. If it is already running, an error will be thrown.
     */
    public resume(): Promise<void>;
    /**
     * Terminate the instance. If it is errored, terminated or complete, an error will be thrown.
     */
    public terminate(): Promise<void>;
    /**
     * Restart the instance.
     */
    public restart(): Promise<void>;
    /**
     * Returns the current status of the instance.
     */
    public status(): Promise<InstanceStatus>;
    /**
     * Send an event to this instance.
     */
    public sendEvent({ type, payload, }: {
        type: string;
        payload: unknown;
    }): Promise<void>;
}



================================================
FILE: wrangler-simple.jsonc
================================================
{
  "name": "simple-math-mcp",
  "main": "src/simple-math.ts",
  "compatibility_date": "2025-03-10",
  "compatibility_flags": [
    "nodejs_compat"
  ],
  "vars": {
    "NODE_ENV": "development"
  },
	"migrations": [
		{
			"new_sqlite_classes": [
				"MyMCP"
			],
			"tag": "v1"
		}
	],  
  "durable_objects": {
    "bindings": [
      {
        "class_name": "MyMCP",
        "name": "MCP_OBJECT"
      }
    ]
  },
  "dev": {
    "port": 8789
  }
}


================================================
FILE: wrangler.jsonc
================================================
/**
 * For more details on how to configure Wrangler, refer to:
 * https://developers.cloudflare.com/workers/wrangler/configuration/
 */
{
	"$schema": "node_modules/wrangler/config-schema.json",
	"name": "my-mcp-server",
	"main": "src/index.ts",
	"compatibility_date": "2025-03-10",
	"compatibility_flags": [
		"nodejs_compat"
	],
	"migrations": [
		{
			"new_sqlite_classes": [
				"MyMCP"
			],
			"tag": "v1"
		}
	],
	"durable_objects": {
		"bindings": [
			{
				"class_name": "MyMCP",
				"name": "MCP_OBJECT"
			}
		]
	},
	"kv_namespaces": [
		{
			"binding": "OAUTH_KV",
			"id": "06998ca39ffb4273a10747065041347b"
		}
	],
	"ai": {
		"binding": "AI"
	},
	"observability": {
		"enabled": true
	},
	"dev": {
		"port": 8792
	}
	/**
	 * Smart Placement
	 * Docs: https://developers.cloudflare.com/workers/configuration/smart-placement/#smart-placement
	 */
	// "placement": { "mode": "smart" },

	/**
	 * Bindings
	 * Bindings allow your Worker to interact with resources on the Cloudflare Developer Platform, including
	 * databases, object storage, AI inference, real-time communication and more.
	 * https://developers.cloudflare.com/workers/runtime-apis/bindings/
	 */

	/**
	 * Environment Variables
	 * https://developers.cloudflare.com/workers/wrangler/configuration/#environment-variables
	 */
	// "vars": { "MY_VARIABLE": "production_value" },
	/**
	 * Note: Use secrets to store sensitive data.
	 * https://developers.cloudflare.com/workers/configuration/secrets/
	 */

	/**
	 * Static Assets
	 * https://developers.cloudflare.com/workers/static-assets/binding/
	 */
	// "assets": { "directory": "./public/", "binding": "ASSETS" },

	/**
	 * Service Bindings (communicate between multiple Workers)
	 * https://developers.cloudflare.com/workers/wrangler/configuration/#service-bindings
	 */
	// "services": [{ "binding": "MY_SERVICE", "service": "my-service" }]
}



================================================
FILE: .dev.vars.example
================================================
GITHUB_CLIENT_ID=<your github client id>
GITHUB_CLIENT_SECRET=<your github client secret>
COOKIE_ENCRYPTION_KEY=<your cookie cookie encryption key>

# Database Connection String
# This should be a PostgreSQL connection string with full read/write permissions
# Format: postgresql://username:password@hostname:port/database_name
# Example: postgresql://user:password@localhost:5432/mydb
# For production, use Hyperdrive: https://developers.cloudflare.com/hyperdrive/
DATABASE_URL=postgresql://username:password@localhost:5432/database_name

# Optional: Add Sentry DSN for local development monitoring
# Get your DSN from https://sentry.io/settings/projects/your-project/keys/
# Create a new project in Sentry, then for the platform pick Cloudflare Workers (search in the top right)
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
NODE_ENV=development



================================================
FILE: .prettierrc
================================================
{
  "printWidth": 140,
  "singleQuote": false,
  "semi": true,
  "useTabs": false,
  "overrides": [
    {
      "files": ["*.jsonc"],
      "options": {
        "trailingComma": "none"
      }
    }
  ]
}



================================================
FILE: PRPs/README.md
================================================
# Product Requirement Prompt (PRP) Concept

"Over-specifying what to build while under-specifying the context, and how to build it, is why so many AI-driven coding attempts stall at 80%. A Product Requirement Prompt (PRP) fixes that by fusing the disciplined scope of a classic Product Requirements Document (PRD) with the “context-is-king” mindset of modern prompt engineering."

## What is a PRP?

Product Requirement Prompt (PRP)
A PRP is a structured prompt that supplies an AI coding agent with everything it needs to deliver a vertical slice of working software—no more, no less.

### How it differs from a PRD

A traditional PRD clarifies what the product must do and why customers need it, but deliberately avoids how it will be built.

A PRP keeps the goal and justification sections of a PRD yet adds three AI-critical layers:

### Context

- Precise file paths and content, library versions and library context, code snippets examples. LLMs generate higher-quality code when given direct, in-prompt references instead of broad descriptions. Usage of a ai_docs/ directory to pipe in library and other docs.

### Implementation Details and Strategy

- In contrast of a traditional PRD, a PRP explicitly states how the product will be built. This includes the use of API endpoints, test runners, or agent patterns (ReAct, Plan-and-Execute) to use. Usage of typehints, dependencies, architectural patterns and other tools to ensure the code is built correctly.

### Validation Gates

- Deterministic checks such as pytest, ruff, or static type passes “Shift-left” quality controls catch defects early and are cheaper than late re-work.
  Example: Each new funtion should be individaully tested, Validation gate = all tests pass.

### PRP Layer Why It Exists

- The PRP folder is used to prepare and pipe PRPs to the agentic coder.

## Why context is non-negotiable

Large-language-model outputs are bounded by their context window; irrelevant or missing context literally squeezes out useful tokens

The industry mantra “Garbage In → Garbage Out” applies doubly to prompt engineering and especially in agentic engineering: sloppy input yields brittle code

## In short

A PRP is PRD + curated codebase intelligence + agent/runbook—the minimum viable packet an AI needs to plausibly ship production-ready code on the first pass.

The PRP can be small and focusing on a single task or large and covering multiple tasks.
The true power of PRP is in the ability to chain tasks together in a PRP to build, self-validate and ship complex features.



================================================
FILE: PRPs/plan.md
================================================
---
Desctiption: This is the plan that was used as a PRP to create the draft /commands for prp-mcp and the prp_mc_base template
---

# MCP Server PRP System Implementation Plan

## Purpose

Build a complete PRP (Product Requirement Prompt) flow specifically designed for creating MCP servers using this codebase as the foundation. This system will enable developers to extremely easily get started with building production-ready MCP servers using Claude Code.

## Core Objectives

1. **Streamlined MCP Development**: Provide a structured approach to build MCP servers with authentication, database integration, and production deployment
2. **Context-Rich PRPs**: Leverage the proven patterns from this codebase to create comprehensive implementation prompts
3. **One-Pass Success**: Enable developers to create working MCP servers through single PRP execution with Claude Code
4. **Best Practices Integration**: Incorporate July 2025 Claude Code patterns (TodoWrite usage, parallel tool calls, CLAUDE.md documentation)

## Implementation Strategy

### Phase 1: Core PRP Commands

**Files to Create:**

- `.claude/commands/prp-mcp-create.md` - Creates MCP server PRPs with deep research
- `.claude/commands/prp-mcp-execute.md` - Executes MCP server PRPs with validation

**Key Features:**

- Specialized research for MCP/Cloudflare Workers/OAuth patterns
- Integration with existing `prp_mcp_server.md` template
- TodoWrite-driven task management following 2025 best practices
- Comprehensive validation gates for MCP server development

### Phase 2: Enhanced Documentation

**Files to Create:**

- `PRPs/ai_docs/mcp_patterns.md` - Core MCP development patterns
- `PRPs/ai_docs/cloudflare_workers_setup.md` - Workers deployment patterns
- `PRPs/ai_docs/oauth_integration.md` - Authentication flow documentation

**Purpose:**

- Provide rich context for PRP generation
- Document common MCP server patterns and gotchas
- Enable AI agents to reference proven implementation approaches

### Phase 3: Validation & Testing Framework

**Enhancements:**

- Extend validation loops with MCP-specific tests
- Add MCP Inspector integration testing
- Claude Desktop configuration validation
- Production deployment verification

### Phase 4: Integration & Optimization

**Integration Points:**

- Seamless workflow with existing PRP base system
- Parallel processing for research and implementation
- Error recovery patterns for MCP-specific failures
- Performance optimizations for large MCP server projects

## Success Metrics

- **Developer Onboarding**: New developers can create working MCP servers in under 30 minutes
- **One-Pass Success Rate**: 90%+ PRP execution success without manual intervention
- **Production Readiness**: Generated MCP servers include authentication, error handling, and monitoring
- **Client Compatibility**: Generated servers work with Claude Desktop, Cursor, and MCP Inspector

## Technical Approach

### Research Integration

- Leverage existing research patterns from `prp-base-create.md`
- Add MCP-specific research for tools, authentication, and deployment
- Integration with Cloudflare Workers documentation and patterns

### Validation Framework

- Multi-level validation from syntax to production deployment
- MCP-specific testing with Inspector and client integration
- Authentication flow validation
- Database integration testing (when applicable)

### Context Management

- Rich documentation pipeline through `ai_docs/` directory
- Integration with existing codebase patterns
- Comprehensive error handling and recovery documentation

## Deliverables

1. **Core Commands** (Phase 1)
   - `prp-mcp-create.md` - MCP server PRP creation
   - `prp-mcp-execute.md` - MCP server PRP execution

2. **Documentation Library** (Phase 2)
   - MCP patterns and best practices
   - Cloudflare Workers setup guides
   - OAuth integration documentation

3. **Validation Suite** (Phase 3)
   - MCP server testing framework
   - Client integration validation
   - Production deployment checks

4. **Integration Package** (Phase 4)
   - Complete workflow documentation
   - Performance optimization
   - Error recovery patterns

## Implementation Timeline

- **Phase 1**: Core PRP commands (Immediate)
- **Phase 2**: Documentation library (Week 1)
- **Phase 3**: Validation framework (Week 2)
- **Phase 4**: Integration & optimization (Week 3)

## Quality Gates

- All commands follow existing PRP patterns
- Integration with TodoWrite tool for task management
- Comprehensive validation loops for MCP development
- Production-ready output with authentication and monitoring
- Compatibility with July 2025 Claude Code best practices

---

_This plan creates a specialized PRP system for MCP server development, building on the proven patterns in this codebase while incorporating the latest Claude Code best practices for maximum developer productivity._



================================================
FILE: PRPs/ai_docs/mcp_patterns.md
================================================
# MCP Server Development Patterns

This document contains proven patterns for developing Model Context Protocol (MCP) servers using TypeScript and Cloudflare Workers, based on the implementation in this codebase.

## Core MCP Server Architecture

### Base Server Class Pattern

```typescript
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Authentication props from OAuth flow
type Props = {
  login: string;
  name: string;
  email: string;
  accessToken: string;
};

export class CustomMCP extends McpAgent<Env, Record<string, never>, Props> {
  server = new McpServer({
    name: "Your MCP Server Name",
    version: "1.0.0",
  });

  // CRITICAL: Implement cleanup for Durable Objects
  async cleanup(): Promise<void> {
    try {
      // Close database connections
      await closeDb();
      console.log('Database connections closed successfully');
    } catch (error) {
      console.error('Error during database cleanup:', error);
    }
  }

  // CRITICAL: Durable Objects alarm handler
  async alarm(): Promise<void> {
    await this.cleanup();
  }

  // Initialize all tools and resources
  async init() {
    // Register tools here
    this.registerTools();
    
    // Register resources if needed
    this.registerResources();
  }

  private registerTools() {
    // Tool registration logic
  }

  private registerResources() {
    // Resource registration logic
  }
}
```

### Tool Registration Pattern

```typescript
// Basic tool registration
this.server.tool(
  "toolName",
  "Tool description for the LLM",
  {
    param1: z.string().describe("Parameter description"),
    param2: z.number().optional().describe("Optional parameter"),
  },
  async ({ param1, param2 }) => {
    try {
      // Tool implementation
      const result = await performOperation(param1, param2);
      
      return {
        content: [
          {
            type: "text",
            text: `Success: ${JSON.stringify(result, null, 2)}`
          }
        ]
      };
    } catch (error) {
      console.error('Tool error:', error);
      return {
        content: [
          {
            type: "text",
            text: `Error: ${error.message}`,
            isError: true
          }
        ]
      };
    }
  }
);
```

### Conditional Tool Registration (Based on Permissions)

```typescript
// Permission-based tool availability
const ALLOWED_USERNAMES = new Set<string>([
  'admin1',
  'admin2'
]);

// Register privileged tools only for authorized users
if (ALLOWED_USERNAMES.has(this.props.login)) {
  this.server.tool(
    "privilegedTool",
    "Tool only available to authorized users",
    { /* parameters */ },
    async (params) => {
      // Privileged operation
      return {
        content: [
          {
            type: "text",
            text: `Privileged operation executed by: ${this.props.login}`
          }
        ]
      };
    }
  );
}
```

## Database Integration Patterns

### Database Connection Pattern

```typescript
import { withDatabase, validateSqlQuery, isWriteOperation, formatDatabaseError } from "./database";

// Database operation with connection management
async function performDatabaseOperation(sql: string) {
  try {
    // Validate SQL query
    const validation = validateSqlQuery(sql);
    if (!validation.isValid) {
      return {
        content: [
          {
            type: "text",
            text: `Invalid SQL query: ${validation.error}`,
            isError: true
          }
        ]
      };
    }

    // Execute with automatic connection management
    return await withDatabase(this.env.DATABASE_URL, async (db) => {
      const results = await db.unsafe(sql);
      
      return {
        content: [
          {
            type: "text",
            text: `**Query Results**\n\`\`\`sql\n${sql}\n\`\`\`\n\n**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\`\n\n**Rows returned:** ${Array.isArray(results) ? results.length : 1}`
          }
        ]
      };
    });
  } catch (error) {
    console.error('Database operation error:', error);
    return {
      content: [
        {
          type: "text",
          text: `Database error: ${formatDatabaseError(error)}`,
          isError: true
        }
      ]
    };
  }
}
```

### Read vs Write Operation Handling

```typescript
// Check if operation is read-only
if (isWriteOperation(sql)) {
  return {
    content: [
      {
        type: "text",
        text: "Write operations are not allowed with this tool. Use the privileged tool if you have write permissions.",
        isError: true
      }
    ]
  };
}
```

## Authentication & Authorization Patterns

### OAuth Integration Pattern

```typescript
import OAuthProvider from "@cloudflare/workers-oauth-provider";
import { GitHubHandler } from "./github-handler";

// OAuth configuration
export default new OAuthProvider({
  apiHandlers: {
    '/sse': MyMCP.serveSSE('/sse') as any,
    '/mcp': MyMCP.serve('/mcp') as any,
  },
  authorizeEndpoint: "/authorize",
  clientRegistrationEndpoint: "/register",
  defaultHandler: GitHubHandler as any,
  tokenEndpoint: "/token",
});
```

### User Permission Checking

```typescript
// Permission validation pattern
function hasPermission(username: string, operation: string): boolean {
  const WRITE_PERMISSIONS = new Set(['admin1', 'admin2']);
  const READ_PERMISSIONS = new Set(['user1', 'user2', ...WRITE_PERMISSIONS]);
  
  switch (operation) {
    case 'read':
      return READ_PERMISSIONS.has(username);
    case 'write':
      return WRITE_PERMISSIONS.has(username);
    default:
      return false;
  }
}
```

## Error Handling Patterns

### Standardized Error Response

```typescript
// Error response pattern
function createErrorResponse(error: Error, operation: string) {
  console.error(`${operation} error:`, error);
  
  return {
    content: [
      {
        type: "text",
        text: `${operation} failed: ${error.message}`,
        isError: true
      }
    ]
  };
}
```

### Database Error Formatting

```typescript
// Use the built-in database error formatter
import { formatDatabaseError } from "./database";

try {
  // Database operation
} catch (error) {
  return {
    content: [
      {
        type: "text",
        text: `Database error: ${formatDatabaseError(error)}`,
        isError: true
      }
    ]
  };
}
```

## Resource Registration Patterns

### Basic Resource Pattern

```typescript
// Resource registration
this.server.resource(
  "resource://example/{id}",
  "Resource description",
  async (uri) => {
    const id = uri.path.split('/').pop();
    
    try {
      const data = await fetchResourceData(id);
      
      return {
        contents: [
          {
            uri: uri.href,
            mimeType: "application/json",
            text: JSON.stringify(data, null, 2)
          }
        ]
      };
    } catch (error) {
      throw new Error(`Failed to fetch resource: ${error.message}`);
    }
  }
);
```

## Testing Patterns

### Tool Testing Pattern

```typescript
// Test tool functionality
async function testTool(toolName: string, params: any) {
  try {
    const result = await server.callTool(toolName, params);
    console.log(`${toolName} test passed:`, result);
    return true;
  } catch (error) {
    console.error(`${toolName} test failed:`, error);
    return false;
  }
}
```

### Database Connection Testing

```typescript
// Test database connectivity
async function testDatabaseConnection() {
  try {
    await withDatabase(process.env.DATABASE_URL, async (db) => {
      const result = await db`SELECT 1 as test`;
      console.log('Database connection test passed:', result);
    });
    return true;
  } catch (error) {
    console.error('Database connection test failed:', error);
    return false;
  }
}
```

## Security Best Practices

### Input Validation

```typescript
// Always validate inputs with Zod
const inputSchema = z.object({
  query: z.string().min(1).max(1000),
  parameters: z.array(z.string()).optional()
});

// In tool handler
try {
  const validated = inputSchema.parse(params);
  // Use validated data
} catch (error) {
  return createErrorResponse(error, "Input validation");
}
```

### SQL Injection Prevention

```typescript
// Use the built-in SQL validation
import { validateSqlQuery } from "./database";

const validation = validateSqlQuery(sql);
if (!validation.isValid) {
  return createErrorResponse(new Error(validation.error), "SQL validation");
}
```

### Access Control

```typescript
// Always check permissions before executing sensitive operations
if (!hasPermission(this.props.login, 'write')) {
  return {
    content: [
      {
        type: "text",
        text: "Access denied: insufficient permissions",
        isError: true
      }
    ]
  };
}
```

## Performance Patterns

### Connection Pooling

```typescript
// Use the built-in connection pooling
import { withDatabase } from "./database";

// The withDatabase function handles connection pooling automatically
await withDatabase(databaseUrl, async (db) => {
  // Database operations
});
```

### Resource Cleanup

```typescript
// Implement proper cleanup in Durable Objects
async cleanup(): Promise<void> {
  try {
    // Close database connections
    await closeDb();
    
    // Clean up other resources
    await cleanupResources();
    
    console.log('Cleanup completed successfully');
  } catch (error) {
    console.error('Cleanup error:', error);
  }
}
```

## Common Gotchas

### 1. Missing Cleanup Implementation
- Always implement `cleanup()` method in Durable Objects
- Handle database connection cleanup properly
- Set up alarm handler for automatic cleanup

### 2. SQL Injection Vulnerabilities
- Always use `validateSqlQuery()` before executing SQL
- Never concatenate user input directly into SQL strings
- Use parameterized queries when possible

### 3. Permission Bypasses
- Check permissions for every sensitive operation
- Don't rely on tool registration alone for security
- Always validate user identity from props

### 4. Error Information Leakage
- Use `formatDatabaseError()` to sanitize error messages
- Don't expose internal system details in error responses
- Log detailed errors server-side, return generic messages to client

### 5. Resource Leaks
- Always use `withDatabase()` for database operations
- Implement proper error handling in async operations
- Clean up resources in finally blocks

## Environment Configuration

### Required Environment Variables

```typescript
// Environment type definition
interface Env {
  DATABASE_URL: string;
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  OAUTH_KV: KVNamespace;
  // Add other bindings as needed
}
```

### Wrangler Configuration Pattern

```toml
# wrangler.toml
name = "mcp-server"
main = "src/index.ts"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "OAUTH_KV"
id = "your-kv-namespace-id"

[env.production]
# Production-specific configuration
```

This document provides the core patterns for building secure, scalable MCP servers using the proven architecture in this codebase.


================================================
FILE: PRPs/templates/prp_mcp_base.md
================================================
---
name: "MCP Server PRP Template"
description: This template is designed to provide a production-ready Model Context Protocol (MCP) server using the proven patterns from this codebase.
---

## Purpose

Template optimized for AI agents to implement production-ready Model Context Protocol (MCP) servers with GitHub OAuth authentication, database integration, and Cloudflare Workers deployment using the proven patterns from this codebase.

## Core Principles

1. **Context is King**: Include ALL necessary MCP patterns, authentication flows, and deployment configurations
2. **Validation Loops**: Provide executable tests from TypeScript compilation to production deployment
3. **Security First**: Build-in authentication, authorization, and SQL injection protection
4. **Production Ready**: Include monitoring, error handling, and deployment automation

---

## Goal

Build a production-ready MCP (Model Context Protocol) server with:

- [SPECIFIC MCP FUNCTIONALITY] - describe the specific tools and resources to implement
- GitHub OAuth authentication with role-based access control
- PostgreSQL database integration with security validation
- Cloudflare Workers deployment with monitoring
- [ADDITIONAL FEATURES] - any specific features beyond the base authentication/database

## Why

- **Developer Productivity**: Enable secure AI assistant access to [SPECIFIC DATA/OPERATIONS]
- **Enterprise Security**: GitHub OAuth with granular permission system
- **Scalability**: Cloudflare Workers global edge deployment
- **Integration**: [HOW THIS FITS WITH EXISTING SYSTEMS]
- **User Value**: [SPECIFIC BENEFITS TO END USERS]

## What

### MCP Server Features

**Core MCP Tools:**

- [LIST SPECIFIC TOOLS] - e.g., "queryDatabase", "listTables", "executeOperations"
- User authentication and permission validation
- Comprehensive error handling and logging
- [DOMAIN-SPECIFIC TOOLS] - tools specific to your use case

**Authentication & Authorization:**

- GitHub OAuth 2.0 integration with signed cookie approval system
- Role-based access control (read-only vs privileged users)
- User context propagation to all MCP tools
- Secure session management with HMAC-signed cookies

**Database Integration:**

- PostgreSQL connection pooling with automatic cleanup
- SQL injection protection and query validation
- Read/write operation separation based on user permissions
- Error sanitization to prevent information leakage

**Deployment & Monitoring:**

- Cloudflare Workers with Durable Objects for state management
- Optional Sentry integration for error tracking and performance monitoring
- Environment-based configuration (development vs production)
- Real-time logging and alerting

### Success Criteria

- [ ] MCP server passes validation with MCP Inspector
- [ ] GitHub OAuth flow works end-to-end (authorization → callback → MCP access)
- [ ] Database operations work with proper permission validation
- [ ] TypeScript compilation succeeds with no errors
- [ ] Local development server starts and responds correctly
- [ ] Production deployment to Cloudflare Workers succeeds
- [ ] Authentication prevents unauthorized access to sensitive operations
- [ ] Error handling provides user-friendly messages without leaking system details
- [ ] [DOMAIN-SPECIFIC SUCCESS CRITERIA]

## All Needed Context

### Documentation & References (MUST READ)

```yaml
# CRITICAL MCP PATTERNS - Read these first
- docfile: PRPs/ai_docs/mcp_patterns.md
  why: Core MCP development patterns, security practices, and error handling

# EXISTING CODEBASE PATTERNS - Study these implementations
- file: src/index.ts
  why: Complete MCP server with authentication, database, and tools - MIRROR this pattern

- file: src/github-handler.ts
  why: OAuth flow implementation - USE this exact pattern for authentication

- file: src/database.ts
  why: Database security, connection pooling, SQL validation - FOLLOW these patterns

- file: src/simple-math.ts
  why: Basic MCP server without auth - good starting point for tool registration

- file: wrangler.jsonc
  why: Cloudflare Workers configuration - COPY this pattern for deployment

# OFFICIAL MCP DOCUMENTATION
- url: https://modelcontextprotocol.io/docs/concepts/tools
  why: MCP tool registration and schema definition patterns

- url: https://modelcontextprotocol.io/docs/concepts/resources
  why: MCP resource implementation if needed

# Add n documentation related to the users use case as needed below
```

### Current Codebase Tree (Run `tree -I node_modules` in project root)

```bash
# INSERT ACTUAL TREE OUTPUT HERE
/
├── src/
│   ├── index.ts                 # Main authenticated MCP server ← STUDY THIS
│   ├── index_sentry.ts         # Sentry monitoring version
│   ├── simple-math.ts          # Basic MCP example ← GOOD STARTING POINT
│   ├── github-handler.ts       # OAuth implementation ← USE THIS PATTERN
│   ├── database.ts             # Database utilities ← SECURITY PATTERNS
│   ├── utils.ts                # OAuth helpers
│   └── workers-oauth-utils.ts  # Cookie security system
├── PRPs/
│   ├── templates/prp_mcp_base.md  # This template
│   └── ai_docs/                   # Implementation guides ← READ ALL
├── wrangler.jsonc              # Cloudflare config ← COPY PATTERNS
├── package.json                # Dependencies
└── tsconfig.json               # TypeScript config
```

### Desired Codebase Tree (Files to add/modify) related to the users use case as needed below

```bash

```

### Known Gotchas & Critical MCP/Cloudflare Patterns

```typescript
// CRITICAL: Cloudflare Workers require specific patterns
// 1. ALWAYS implement cleanup for Durable Objects
export class YourMCP extends McpAgent<Env, Record<string, never>, Props> {
  async cleanup(): Promise<void> {
    await closeDb(); // CRITICAL: Close database connections
  }

  async alarm(): Promise<void> {
    await this.cleanup(); // CRITICAL: Handle Durable Object alarms
  }
}

// 2. ALWAYS validate SQL to prevent injection (use existing patterns)
const validation = validateSqlQuery(sql); // from src/database.ts
if (!validation.isValid) {
  return createErrorResponse(validation.error);
}

// 3. ALWAYS check permissions before sensitive operations
const ALLOWED_USERNAMES = new Set(["admin1", "admin2"]);
if (!ALLOWED_USERNAMES.has(this.props.login)) {
  return createErrorResponse("Insufficient permissions");
}

// 4. ALWAYS use withDatabase wrapper for connection management
return await withDatabase(this.env.DATABASE_URL, async (db) => {
  // Database operations here
});

// 5. ALWAYS use Zod for input validation
import { z } from "zod";
const schema = z.object({
  param: z.string().min(1).max(100),
});

// 6. TypeScript compilation requires exact interface matching
interface Env {
  DATABASE_URL: string;
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  OAUTH_KV: KVNamespace;
  // Add your environment variables here
}
```

## Implementation Blueprint

### Data Models & Types

Define TypeScript interfaces and Zod schemas for type safety and validation.

```typescript
// User authentication props (inherited from OAuth)
type Props = {
  login: string; // GitHub username
  name: string; // Display name
  email: string; // Email address
  accessToken: string; // GitHub access token
};

// MCP tool input schemas (customize for your tools)
const YourToolSchema = z.object({
  param1: z.string().min(1, "Parameter cannot be empty"),
  param2: z.number().int().positive().optional(),
  options: z.object({}).optional(),
});

// Environment interface (add your variables)
interface Env {
  DATABASE_URL: string;
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  OAUTH_KV: KVNamespace;
  // YOUR_SPECIFIC_ENV_VAR: string;
}

// Permission levels (customize for your use case)
enum Permission {
  READ = "read",
  WRITE = "write",
  ADMIN = "admin",
}
```

### List of Tasks (Complete in order)

```yaml
Task 1 - Project Setup:
  COPY wrangler.jsonc to wrangler-[server-name].jsonc:
    - MODIFY name field to "[server-name]"
    - ADD any new environment variables to vars section
    - KEEP existing OAuth and database configuration

  CREATE .dev.vars file (if not exists):
    - ADD GITHUB_CLIENT_ID=your_client_id
    - ADD GITHUB_CLIENT_SECRET=your_client_secret
    - ADD DATABASE_URL=postgresql://...
    - ADD COOKIE_ENCRYPTION_KEY=your_32_byte_key
    - ADD any domain-specific environment variables

Task 2 - GitHub OAuth App:
  CREATE new GitHub OAuth app:
    - SET homepage URL: https://your-worker.workers.dev
    - SET callback URL: https://your-worker.workers.dev/callback
    - COPY client ID and secret to .dev.vars

  OR REUSE existing OAuth app:
    - UPDATE callback URL if using different subdomain
    - VERIFY client ID and secret in environment

Task 3 - MCP Server Implementation:
  CREATE src/[server-name].ts OR MODIFY src/index.ts:
    - COPY class structure from src/index.ts
    - MODIFY server name and version in McpServer constructor
    - IMPLEMENT your domain-specific tools using existing patterns
    - KEEP authentication and database patterns identical

  IMPLEMENT MCP tools:
    - MIRROR tool registration pattern from src/index.ts
    - USE Zod schemas for input validation
    - IMPLEMENT proper error handling with createErrorResponse
    - ADD permission checking for sensitive operations

Task 4 - Database Integration (if needed):
  USE existing database patterns from src/database.ts:
    - IMPORT withDatabase, validateSqlQuery, isWriteOperation
    - IMPLEMENT database operations with security validation
    - SEPARATE read vs write operations based on user permissions
    - USE formatDatabaseError for user-friendly error messages

Task 5 - Environment Configuration:
  SETUP Cloudflare KV namespace:
    - RUN: wrangler kv namespace create "OAUTH_KV"
    - UPDATE wrangler.jsonc with returned namespace ID

  SET production secrets:
    - RUN: wrangler secret put GITHUB_CLIENT_ID
    - RUN: wrangler secret put GITHUB_CLIENT_SECRET
    - RUN: wrangler secret put DATABASE_URL
    - RUN: wrangler secret put COOKIE_ENCRYPTION_KEY

Task 6 - Local Testing:
  TEST basic functionality:
    - RUN: wrangler dev
    - VERIFY server starts without errors
    - TEST OAuth flow: http://localhost:8788/authorize
    - VERIFY MCP endpoint: http://localhost:8788/mcp

Task 7 - Production Deployment:
  DEPLOY to Cloudflare Workers:
    - RUN: wrangler deploy
    - VERIFY deployment success
    - TEST production OAuth flow
    - VERIFY MCP endpoint accessibility
```

### Per Task Implementation Details

```typescript
// Task 3 - MCP Server Implementation Pattern
export class YourMCP extends McpAgent<Env, Record<string, never>, Props> {
  server = new McpServer({
    name: "Your MCP Server Name",
    version: "1.0.0",
  });

  // CRITICAL: Always implement cleanup
  async cleanup(): Promise<void> {
    try {
      await closeDb();
      console.log("Database connections closed successfully");
    } catch (error) {
      console.error("Error during database cleanup:", error);
    }
  }

  async alarm(): Promise<void> {
    await this.cleanup();
  }

  async init() {
    // PATTERN: Register basic tools available to all authenticated users
    this.registerBasicTools();

    // PATTERN: Register privileged tools based on user permissions
    this.registerPrivilegedTools();
  }

  private registerBasicTools() {
    this.server.tool(
      "yourBasicTool",
      "Description of your basic tool",
      YourToolSchema, // Zod validation schema
      async ({ param1, param2, options }) => {
        try {
          // PATTERN: Tool implementation with error handling
          const result = await performOperation(param1, param2, options);

          return {
            content: [
              {
                type: "text",
                text: `**Success**\n\nOperation completed\n\n**Result:**\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\``,
              },
            ],
          };
        } catch (error) {
          return createErrorResponse(`Operation failed: ${error.message}`);
        }
      },
    );
  }

  private registerPrivilegedTools() {
    // PATTERN: Permission-based tool registration
    const PRIVILEGED_USERS = new Set(["admin1", "admin2"]);

    if (PRIVILEGED_USERS.has(this.props.login)) {
      this.server.tool("privilegedTool", "Administrative tool for privileged users", { action: z.string() }, async ({ action }) => {
        // PATTERN: Double-check permissions in tool handler
        if (!PRIVILEGED_USERS.has(this.props.login)) {
          return createErrorResponse("Insufficient permissions");
        }

        // Implement privileged operation
        return {
          content: [
            {
              type: "text",
              text: `Admin action '${action}' executed by ${this.props.login}`,
            },
          ],
        };
      });
    }
  }
}

// PATTERN: Export OAuth provider with MCP endpoints
export default new OAuthProvider({
  apiHandlers: {
    "/sse": YourMCP.serveSSE("/sse") as any,
    "/mcp": YourMCP.serve("/mcp") as any,
  },
  authorizeEndpoint: "/authorize",
  clientRegistrationEndpoint: "/register",
  defaultHandler: GitHubHandler as any,
  tokenEndpoint: "/token",
});
```

### Integration Points

```yaml
CLOUDFLARE_WORKERS:
  - wrangler.jsonc: Update name, environment variables, KV bindings
  - Environment secrets: GitHub OAuth credentials, database URL, encryption key
  - Durable Objects: Configure MCP agent binding for state persistence

GITHUB_OAUTH:
  - GitHub App: Create with callback URL matching your Workers domain
  - Client credentials: Store as Cloudflare Workers secrets
  - Callback URL: Must match exactly: https://your-worker.workers.dev/callback

DATABASE:
  - PostgreSQL connection: Use existing connection pooling patterns
  - Environment variable: DATABASE_URL with full connection string
  - Security: Use validateSqlQuery and isWriteOperation for all SQL

ENVIRONMENT_VARIABLES:
  - Development: .dev.vars file for local testing
  - Production: Cloudflare Workers secrets for deployment
  - Required: GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET, DATABASE_URL, COOKIE_ENCRYPTION_KEY

KV_STORAGE:
  - OAuth state: Used by OAuth provider for state management
  - Namespace: Create with `wrangler kv namespace create "OAUTH_KV"`
  - Configuration: Add namespace ID to wrangler.jsonc bindings
```

## Validation Loop

### Level 1: TypeScript & Configuration

```bash
# CRITICAL: Run these FIRST - fix any errors before proceeding
npm run type-check                 # TypeScript compilation
wrangler types                     # Generate Cloudflare Workers types

# Expected: No TypeScript errors
# If errors: Fix type issues, missing interfaces, import problems
```

### Level 2: Local Development Testing

```bash
# Start local development server
wrangler dev

# Test OAuth flow (should redirect to GitHub)
curl -v http://localhost:8788/authorize

# Test MCP endpoint (should return server info)
curl -v http://localhost:8788/mcp

# Expected: Server starts, OAuth redirects to GitHub, MCP responds with server info
# If errors: Check console output, verify environment variables, fix configuration
```

### Level 4: Database Integration Testing (if applicable)

```bash
# Test database connection
curl -X POST http://localhost:8788/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "listTables", "arguments": {}}}'

# Test permission validation
# Test SQL injection protection
# Test error handling for database failures

# Expected: Database operations work, permissions enforced, errors handled gracefully
# If errors: Check DATABASE_URL, connection settings, permission logic
```

## Final Validation Checklist

### Core Functionality

- [ ] TypeScript compilation: `npm run type-check` passes
- [ ] Local server starts: `wrangler dev` runs without errors
- [ ] MCP endpoint responds: `curl http://localhost:8788/mcp` returns server info
- [ ] OAuth flow works: Authentication redirects and completes successfully

---

## Anti-Patterns to Avoid

### MCP-Specific

- ❌ Don't skip input validation with Zod - always validate tool parameters
- ❌ Don't forget to implement cleanup() method for Durable Objects
- ❌ Don't hardcode user permissions - use configurable permission systems

### Development Process

- ❌ Don't skip the validation loops - each level catches different issues
- ❌ Don't guess about OAuth configuration - test the full flow
- ❌ Don't deploy without monitoring - implement logging and error tracking
- ❌ Don't ignore TypeScript errors - fix all type issues before deployment



================================================
FILE: src/index.ts
================================================
import OAuthProvider from "@cloudflare/workers-oauth-provider";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { Props } from "./types";
import { GitHubHandler } from "./auth/github-handler";
import { closeDb } from "./database/connection";
import { registerAllTools } from "./tools/register-tools";

export class MyMCP extends McpAgent<Env, Record<string, never>, Props> {
	server = new McpServer({
		name: "PostgreSQL Database MCP Server",
		version: "1.0.0",
	});

	/**
	 * Cleanup database connections when Durable Object is shutting down
	 */
	async cleanup(): Promise<void> {
		try {
			await closeDb();
			console.log('Database connections closed successfully');
		} catch (error) {
			console.error('Error during database cleanup:', error);
		}
	}

	/**
	 * Durable Objects alarm handler - used for cleanup
	 */
	async alarm(): Promise<void> {
		await this.cleanup();
	}

	async init() {
		// Register all tools based on user permissions
		registerAllTools(this.server, this.env, this.props);
	}
}

export default new OAuthProvider({
	apiHandlers: {
		'/sse': MyMCP.serveSSE('/sse') as any,
		'/mcp': MyMCP.serve('/mcp') as any,
	},
	authorizeEndpoint: "/authorize",
	clientRegistrationEndpoint: "/register",
	defaultHandler: GitHubHandler as any,
	tokenEndpoint: "/token",
});


================================================
FILE: src/index_sentry.ts
================================================
import * as Sentry from "@sentry/cloudflare";
import OAuthProvider from "@cloudflare/workers-oauth-provider";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { McpAgent } from "agents/mcp";
import { Props } from "./types";
import { GitHubHandler } from "./auth/github-handler";
import { closeDb } from "./database/connection";
import { registerDatabaseToolsWithSentry } from "./tools/database-tools-sentry";

// Sentry configuration helper
function getSentryConfig(env: Env) {
	return {
		// You can disable Sentry by setting SENTRY_DSN to a falsey-value
		dsn: (env as any).SENTRY_DSN,
		// A sample rate of 1.0 means "capture all traces"
		tracesSampleRate: 1,
	};
}

export class MyMCP extends McpAgent<Env, Record<string, never>, Props> {
	server = new McpServer({
		name: "PostgreSQL Database MCP Server",
		version: "1.0.0",
	});

	/**
	 * Cleanup database connections when Durable Object is shutting down
	 */
	async cleanup(): Promise<void> {
		try {
			await closeDb();
			console.log('Database connections closed successfully');
		} catch (error) {
			console.error('Error during database cleanup:', error);
		}
	}

	/**
	 * Durable Objects alarm handler - used for cleanup
	 */
	async alarm(): Promise<void> {
		await this.cleanup();
	}

	async init() {
		// Initialize Sentry
		const sentryConfig = getSentryConfig(this.env);
		if (sentryConfig.dsn) {
			// @ts-ignore - Sentry.init exists but types may not be complete
			Sentry.init(sentryConfig);
		}

		// Register all tools with Sentry instrumentation
		registerDatabaseToolsWithSentry(this.server, this.env, this.props);
	}
}

export default new OAuthProvider({
	apiHandlers: {
		'/sse': MyMCP.serveSSE('/sse') as any,
		'/mcp': MyMCP.serve('/mcp') as any,
	},
	authorizeEndpoint: "/authorize",
	clientRegistrationEndpoint: "/register",
	defaultHandler: GitHubHandler as any,
	tokenEndpoint: "/token",
});


================================================
FILE: src/simple-math.ts
================================================
import { McpAgent } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";

// Define our MCP agent with tools
export class MyMCP extends McpAgent<Env, Record<string, never>, Record<string, never>> {
    server = new McpServer({
        name: "Simple Math Calculator",
        version: "1.0.0",
    });

    async init() {
        // Calculator tool with multiple operations
        this.server.tool(
            "calculate",
            {
                operation: z.enum(["add", "subtract", "multiply", "divide"]),
                a: z.number(),
                b: z.number(),
            },
            async ({ operation, a, b }) => {
                let result: number;
                switch (operation) {
                    case "add":
                        result = a + b;
                        break;
                    case "subtract":
                        result = a - b;
                        break;
                    case "multiply":
                        result = a * b;
                        break;
                    case "divide":
                        if (b === 0)
                            return {
                                content: [
                                    {
                                        type: "text",
                                        text: "Error: Cannot divide by zero",
                                    },
                                ],
                            };
                        result = a / b;
                        break;
                }
                return { content: [{ type: "text", text: String(result) }] };
            }
        );
    }
}

export default {
    fetch(request: Request, env: Env, ctx: ExecutionContext) {
        const url = new URL(request.url);

        if (url.pathname === "/sse" || url.pathname === "/sse/message") {
            return MyMCP.serveSSE("/sse").fetch(request, env, ctx);
        }

        if (url.pathname === "/mcp") {
            return MyMCP.serve("/mcp").fetch(request, env, ctx);
        }

        return new Response("Not found", { status: 404 });
    },
};


================================================
FILE: src/types.ts
================================================
import { z } from "zod";
import type { AuthRequest, OAuthHelpers, ClientInfo } from "@cloudflare/workers-oauth-provider";

// User context passed through OAuth
export type Props = {
  login: string;
  name: string;
  email: string;
  accessToken: string;
};

// Extended environment with OAuth provider
export type ExtendedEnv = Env & { OAUTH_PROVIDER: OAuthHelpers };

// OAuth URL construction parameters
export interface UpstreamAuthorizeParams {
  upstream_url: string;
  client_id: string;
  scope: string;
  redirect_uri: string;
  state?: string;
}

// OAuth token exchange parameters
export interface UpstreamTokenParams {
  code: string | undefined;
  upstream_url: string;
  client_secret: string;
  redirect_uri: string;
  client_id: string;
}

// Approval dialog configuration
export interface ApprovalDialogOptions {
  client: ClientInfo | null;
  server: {
    name: string;
    logo?: string;
    description?: string;
  };
  state: Record<string, any>;
  cookieName?: string;
  cookieSecret?: string | Uint8Array;
  cookieDomain?: string;
  cookiePath?: string;
  cookieMaxAge?: number;
}

// Result of parsing approval form
export interface ParsedApprovalResult {
  state: any;
  headers: Record<string, string>;
}

// MCP tool schemas using Zod
export const ListTablesSchema = {};

export const QueryDatabaseSchema = {
  sql: z
    .string()
    .min(1, "SQL query cannot be empty")
    .describe("SQL query to execute (SELECT queries only)"),
};

export const ExecuteDatabaseSchema = {
  sql: z
    .string()
    .min(1, "SQL command cannot be empty")
    .describe("SQL command to execute (INSERT, UPDATE, DELETE, CREATE, etc.)"),
};

// MCP response types
export interface McpTextContent {
  type: "text";
  text: string;
  isError?: boolean;
}

export interface McpResponse {
  content: McpTextContent[];
}

// Standard response creators
export function createSuccessResponse(message: string, data?: any): McpResponse {
  let text = `**Success**\n\n${message}`;
  if (data !== undefined) {
    text += `\n\n**Result:**\n\`\`\`json\n${JSON.stringify(data, null, 2)}\n\`\`\``;
  }
  return {
    content: [{
      type: "text",
      text,
    }],
  };
}

export function createErrorResponse(message: string, details?: any): McpResponse {
  let text = `**Error**\n\n${message}`;
  if (details !== undefined) {
    text += `\n\n**Details:**\n\`\`\`json\n${JSON.stringify(details, null, 2)}\n\`\`\``;
  }
  return {
    content: [{
      type: "text",
      text,
      isError: true,
    }],
  };
}

// Database operation result type
export interface DatabaseOperationResult<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  duration?: number;
}

// SQL validation result
export interface SqlValidationResult {
  isValid: boolean;
  error?: string;
}

// Re-export external types that are used throughout
export type { AuthRequest, OAuthHelpers, ClientInfo };


================================================
FILE: src/auth/github-handler.ts
================================================
// import { env } from "cloudflare:workers";
import type { AuthRequest } from "@cloudflare/workers-oauth-provider";
import { Hono } from "hono";
import { Octokit } from "octokit";
import type { Props, ExtendedEnv } from "../types";
import {
	clientIdAlreadyApproved,
	parseRedirectApproval,
	renderApprovalDialog,
	fetchUpstreamAuthToken,
	getUpstreamAuthorizeUrl,
} from "./oauth-utils";
const app = new Hono<{ Bindings: ExtendedEnv }>();

app.get("/authorize", async (c) => {
	const oauthReqInfo = await c.env.OAUTH_PROVIDER.parseAuthRequest(c.req.raw);
	const { clientId } = oauthReqInfo;
	if (!clientId) {
		return c.text("Invalid request", 400);
	}

	if (
		await clientIdAlreadyApproved(c.req.raw, oauthReqInfo.clientId, (c.env as any).COOKIE_ENCRYPTION_KEY)
	) {
		return redirectToGithub(c.req.raw, oauthReqInfo, c.env, {});
	}

	return renderApprovalDialog(c.req.raw, {
		client: await c.env.OAUTH_PROVIDER.lookupClient(clientId),
		server: {
			description: "This is a demo MCP Remote Server using GitHub for authentication.",
			logo: "https://avatars.githubusercontent.com/u/314135?s=200&v=4",
			name: "Cloudflare GitHub MCP Server", // optional
		},
		state: { oauthReqInfo }, // arbitrary data that flows through the form submission below
	});
});

app.post("/authorize", async (c) => {
	// Validates form submission, extracts state, and generates Set-Cookie headers to skip approval dialog next time
	const { state, headers } = await parseRedirectApproval(c.req.raw, (c.env as any).COOKIE_ENCRYPTION_KEY);
	if (!state.oauthReqInfo) {
		return c.text("Invalid request", 400);
	}

	return redirectToGithub(c.req.raw, state.oauthReqInfo, c.env, headers);
});

async function redirectToGithub(
	request: Request,
	oauthReqInfo: AuthRequest,
	env: Env,
	headers: Record<string, string> = {},
) {
	return new Response(null, {
		headers: {
			...headers,
			location: getUpstreamAuthorizeUrl({
				client_id: (env as any).GITHUB_CLIENT_ID,
				redirect_uri: new URL("/callback", request.url).href,
				scope: "read:user",
				state: btoa(JSON.stringify(oauthReqInfo)),
				upstream_url: "https://github.com/login/oauth/authorize",
			}),
		},
		status: 302,
	});
}

/**
 * OAuth Callback Endpoint
 *
 * This route handles the callback from GitHub after user authentication.
 * It exchanges the temporary code for an access token, then stores some
 * user metadata & the auth token as part of the 'props' on the token passed
 * down to the client. It ends by redirecting the client back to _its_ callback URL
 */
app.get("/callback", async (c) => {
	// Get the oathReqInfo out of KV
	const oauthReqInfo = JSON.parse(atob(c.req.query("state") as string)) as AuthRequest;
	if (!oauthReqInfo.clientId) {
		return c.text("Invalid state", 400);
	}

	// Exchange the code for an access token
	const [accessToken, errResponse] = await fetchUpstreamAuthToken({
		client_id: (c.env as any).GITHUB_CLIENT_ID,
		client_secret: (c.env as any).GITHUB_CLIENT_SECRET,
		code: c.req.query("code"),
		redirect_uri: new URL("/callback", c.req.url).href,
		upstream_url: "https://github.com/login/oauth/access_token",
	});
	if (errResponse) return errResponse;

	// Fetch the user info from GitHub
	const user = await new Octokit({ auth: accessToken }).rest.users.getAuthenticated();
	const { login, name, email } = user.data;

	// Return back to the MCP client a new token
	const { redirectTo } = await c.env.OAUTH_PROVIDER.completeAuthorization({
		metadata: {
			label: name,
		},
		// This will be available on this.props inside MyMCP
		props: {
			accessToken,
			email,
			login,
			name,
		} as Props,
		request: oauthReqInfo,
		scope: oauthReqInfo.scope,
		userId: login,
	});

	return Response.redirect(redirectTo);
});

export { app as GitHubHandler };



================================================
FILE: src/auth/oauth-utils.ts
================================================
// OAuth utilities for cookie-based approval and upstream OAuth flows

import type { 
  AuthRequest, 
  ClientInfo,
  ApprovalDialogOptions,
  ParsedApprovalResult,
  UpstreamAuthorizeParams,
  UpstreamTokenParams 
} from "../types";

const COOKIE_NAME = "mcp-approved-clients";
const ONE_YEAR_IN_SECONDS = 31536000;

// --- Helper Functions ---

/**
 * Encodes arbitrary data to a URL-safe base64 string.
 * @param data - The data to encode (will be stringified).
 * @returns A URL-safe base64 encoded string.
 */
function _encodeState(data: any): string {
	try {
		const jsonString = JSON.stringify(data);
		// Use btoa for simplicity, assuming Worker environment supports it well enough
		// For complex binary data, a Buffer/Uint8Array approach might be better
		return btoa(jsonString);
	} catch (e) {
		console.error("Error encoding state:", e);
		throw new Error("Could not encode state");
	}
}

/**
 * Decodes a URL-safe base64 string back to its original data.
 * @param encoded - The URL-safe base64 encoded string.
 * @returns The original data.
 */
function decodeState<T = any>(encoded: string): T {
	try {
		const jsonString = atob(encoded);
		return JSON.parse(jsonString);
	} catch (e) {
		console.error("Error decoding state:", e);
		throw new Error("Could not decode state");
	}
}

/**
 * Imports a secret key string for HMAC-SHA256 signing.
 * @param secret - The raw secret key string.
 * @returns A promise resolving to the CryptoKey object.
 */
async function importKey(secret: string): Promise<CryptoKey> {
	if (!secret) {
		throw new Error(
			"COOKIE_SECRET is not defined. A secret key is required for signing cookies.",
		);
	}
	const enc = new TextEncoder();
	return crypto.subtle.importKey(
		"raw",
		enc.encode(secret),
		{ hash: "SHA-256", name: "HMAC" },
		false, // not extractable
		["sign", "verify"], // key usages
	);
}

/**
 * Signs data using HMAC-SHA256.
 * @param key - The CryptoKey for signing.
 * @param data - The string data to sign.
 * @returns A promise resolving to the signature as a hex string.
 */
async function signData(key: CryptoKey, data: string): Promise<string> {
	const enc = new TextEncoder();
	const signatureBuffer = await crypto.subtle.sign("HMAC", key, enc.encode(data));
	// Convert ArrayBuffer to hex string
	return Array.from(new Uint8Array(signatureBuffer))
		.map((b) => b.toString(16).padStart(2, "0"))
		.join("");
}

/**
 * Verifies an HMAC-SHA256 signature.
 * @param key - The CryptoKey for verification.
 * @param signatureHex - The signature to verify (hex string).
 * @param data - The original data that was signed.
 * @returns A promise resolving to true if the signature is valid, false otherwise.
 */
async function verifySignature(
	key: CryptoKey,
	signatureHex: string,
	data: string,
): Promise<boolean> {
	const enc = new TextEncoder();
	try {
		// Convert hex signature back to ArrayBuffer
		const signatureBytes = new Uint8Array(
			signatureHex.match(/.{1,2}/g)!.map((byte) => Number.parseInt(byte, 16)),
		);
		return await crypto.subtle.verify("HMAC", key, signatureBytes.buffer, enc.encode(data));
	} catch (e) {
		// Handle errors during hex parsing or verification
		console.error("Error verifying signature:", e);
		return false;
	}
}

/**
 * Parses the signed cookie and verifies its integrity.
 * @param cookieHeader - The value of the Cookie header from the request.
 * @param secret - The secret key used for signing.
 * @returns A promise resolving to the list of approved client IDs if the cookie is valid, otherwise null.
 */
async function getApprovedClientsFromCookie(
	cookieHeader: string | null,
	secret: string,
): Promise<string[] | null> {
	if (!cookieHeader) return null;

	const cookies = cookieHeader.split(";").map((c) => c.trim());
	const targetCookie = cookies.find((c) => c.startsWith(`${COOKIE_NAME}=`));

	if (!targetCookie) return null;

	const cookieValue = targetCookie.substring(COOKIE_NAME.length + 1);
	const parts = cookieValue.split(".");

	if (parts.length !== 2) {
		console.warn("Invalid cookie format received.");
		return null; // Invalid format
	}

	const [signatureHex, base64Payload] = parts;
	const payload = atob(base64Payload); // Assuming payload is base64 encoded JSON string

	const key = await importKey(secret);
	const isValid = await verifySignature(key, signatureHex, payload);

	if (!isValid) {
		console.warn("Cookie signature verification failed.");
		return null; // Signature invalid
	}

	try {
		const approvedClients = JSON.parse(payload);
		if (!Array.isArray(approvedClients)) {
			console.warn("Cookie payload is not an array.");
			return null; // Payload isn't an array
		}
		// Ensure all elements are strings
		if (!approvedClients.every((item) => typeof item === "string")) {
			console.warn("Cookie payload contains non-string elements.");
			return null;
		}
		return approvedClients as string[];
	} catch (e) {
		console.error("Error parsing cookie payload:", e);
		return null; // JSON parsing failed
	}
}

// --- Exported Functions ---

/**
 * Checks if a given client ID has already been approved by the user,
 * based on a signed cookie.
 *
 * @param request - The incoming Request object to read cookies from.
 * @param clientId - The OAuth client ID to check approval for.
 * @param cookieSecret - The secret key used to sign/verify the approval cookie.
 * @returns A promise resolving to true if the client ID is in the list of approved clients in a valid cookie, false otherwise.
 */
export async function clientIdAlreadyApproved(
	request: Request,
	clientId: string,
	cookieSecret: string,
): Promise<boolean> {
	if (!clientId) return false;
	const cookieHeader = request.headers.get("Cookie");
	const approvedClients = await getApprovedClientsFromCookie(cookieHeader, cookieSecret);

	return approvedClients?.includes(clientId) ?? false;
}


/**
 * Renders an approval dialog for OAuth authorization
 * The dialog displays information about the client and server
 * and includes a form to submit approval
 *
 * @param request - The HTTP request
 * @param options - Configuration for the approval dialog
 * @returns A Response containing the HTML approval dialog
 */
export function renderApprovalDialog(request: Request, options: ApprovalDialogOptions): Response {
	const { client, server, state } = options;

	// Encode state for form submission
	const encodedState = btoa(JSON.stringify(state));

	// Sanitize any untrusted content
	const serverName = sanitizeHtml(server.name);
	const clientName = client?.clientName ? sanitizeHtml(client.clientName) : "Unknown MCP Client";
	const serverDescription = server.description ? sanitizeHtml(server.description) : "";

	// Safe URLs
	const logoUrl = server.logo ? sanitizeHtml(server.logo) : "";
	const clientUri = client?.clientUri ? sanitizeHtml(client.clientUri) : "";
	const policyUri = client?.policyUri ? sanitizeHtml(client.policyUri) : "";
	const tosUri = client?.tosUri ? sanitizeHtml(client.tosUri) : "";

	// Client contacts
	const contacts =
		client?.contacts && client.contacts.length > 0
			? sanitizeHtml(client.contacts.join(", "))
			: "";

	// Get redirect URIs
	const redirectUris =
		client?.redirectUris && client.redirectUris.length > 0
			? client.redirectUris.map((uri) => sanitizeHtml(uri))
			: [];

	// Generate HTML for the approval dialog
	const htmlContent = `
    <!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${clientName} | Authorization Request</title>
        <style>
          /* Modern, responsive styling with system fonts */
          :root {
            --primary-color: #0070f3;
            --error-color: #f44336;
            --border-color: #e5e7eb;
            --text-color: #333;
            --background-color: #fff;
            --card-shadow: 0 8px 36px 8px rgba(0, 0, 0, 0.1);
          }
          
          body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
                         Helvetica, Arial, sans-serif, "Apple Color Emoji", 
                         "Segoe UI Emoji", "Segoe UI Symbol";
            line-height: 1.6;
            color: var(--text-color);
            background-color: #f9fafb;
            margin: 0;
            padding: 0;
          }
          
          .container {
            max-width: 600px;
            margin: 2rem auto;
            padding: 1rem;
          }
          
          .precard {
            padding: 2rem;
            text-align: center;
          }
          
          .card {
            background-color: var(--background-color);
            border-radius: 8px;
            box-shadow: var(--card-shadow);
            padding: 2rem;
          }
          
          .header {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
          }
          
          .logo {
            width: 48px;
            height: 48px;
            margin-right: 1rem;
            border-radius: 8px;
            object-fit: contain;
          }
          
          .title {
            margin: 0;
            font-size: 1.3rem;
            font-weight: 400;
          }
          
          .alert {
            margin: 0;
            font-size: 1.5rem;
            font-weight: 400;
            margin: 1rem 0;
            text-align: center;
          }
          
          .description {
            color: #555;
          }
          
          .client-info {
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 1rem 1rem 0.5rem;
            margin-bottom: 1.5rem;
          }
          
          .client-name {
            font-weight: 600;
            font-size: 1.2rem;
            margin: 0 0 0.5rem 0;
          }
          
          .client-detail {
            display: flex;
            margin-bottom: 0.5rem;
            align-items: baseline;
          }
          
          .detail-label {
            font-weight: 500;
            min-width: 120px;
          }
          
          .detail-value {
            font-family: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
            word-break: break-all;
          }
          
          .detail-value a {
            color: inherit;
            text-decoration: underline;
          }
          
          .detail-value.small {
            font-size: 0.8em;
          }
          
          .external-link-icon {
            font-size: 0.75em;
            margin-left: 0.25rem;
            vertical-align: super;
          }
          
          .actions {
            display: flex;
            justify-content: flex-end;
            gap: 1rem;
            margin-top: 2rem;
          }
          
          .button {
            padding: 0.75rem 1.5rem;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            border: none;
            font-size: 1rem;
          }
          
          .button-primary {
            background-color: var(--primary-color);
            color: white;
          }
          
          .button-secondary {
            background-color: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-color);
          }
          
          /* Responsive adjustments */
          @media (max-width: 640px) {
            .container {
              margin: 1rem auto;
              padding: 0.5rem;
            }
            
            .card {
              padding: 1.5rem;
            }
            
            .client-detail {
              flex-direction: column;
            }
            
            .detail-label {
              min-width: unset;
              margin-bottom: 0.25rem;
            }
            
            .actions {
              flex-direction: column;
            }
            
            .button {
              width: 100%;
            }
          }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="precard">
            <div class="header">
              ${logoUrl ? `<img src="${logoUrl}" alt="${serverName} Logo" class="logo">` : ""}
            <h1 class="title"><strong>${serverName}</strong></h1>
            </div>
            
            ${serverDescription ? `<p class="description">${serverDescription}</p>` : ""}
          </div>
            
          <div class="card">
            
            <h2 class="alert"><strong>${clientName || "A new MCP Client"}</strong> is requesting access</h1>
            
            <div class="client-info">
              <div class="client-detail">
                <div class="detail-label">Name:</div>
                <div class="detail-value">
                  ${clientName}
                </div>
              </div>
              
              ${
					clientUri
						? `
                <div class="client-detail">
                  <div class="detail-label">Website:</div>
                  <div class="detail-value small">
                    <a href="${clientUri}" target="_blank" rel="noopener noreferrer">
                      ${clientUri}
                    </a>
                  </div>
                </div>
              `
						: ""
				}
              
              ${
					policyUri
						? `
                <div class="client-detail">
                  <div class="detail-label">Privacy Policy:</div>
                  <div class="detail-value">
                    <a href="${policyUri}" target="_blank" rel="noopener noreferrer">
                      ${policyUri}
                    </a>
                  </div>
                </div>
              `
						: ""
				}
              
              ${
					tosUri
						? `
                <div class="client-detail">
                  <div class="detail-label">Terms of Service:</div>
                  <div class="detail-value">
                    <a href="${tosUri}" target="_blank" rel="noopener noreferrer">
                      ${tosUri}
                    </a>
                  </div>
                </div>
              `
						: ""
				}
              
              ${
					redirectUris.length > 0
						? `
                <div class="client-detail">
                  <div class="detail-label">Redirect URIs:</div>
                  <div class="detail-value small">
                    ${redirectUris.map((uri) => `<div>${uri}</div>`).join("")}
                  </div>
                </div>
              `
						: ""
				}
              
              ${
					contacts
						? `
                <div class="client-detail">
                  <div class="detail-label">Contact:</div>
                  <div class="detail-value">${contacts}</div>
                </div>
              `
						: ""
				}
            </div>
            
            <p>This MCP Client is requesting to be authorized on ${serverName}. If you approve, you will be redirected to complete authentication.</p>
            
            <form method="post" action="${new URL(request.url).pathname}">
              <input type="hidden" name="state" value="${encodedState}">
              
              <div class="actions">
                <button type="button" class="button button-secondary" onclick="window.history.back()">Cancel</button>
                <button type="submit" class="button button-primary">Approve</button>
              </div>
            </form>
          </div>
        </div>
      </body>
    </html>
  `;

	return new Response(htmlContent, {
		headers: {
			"Content-Type": "text/html; charset=utf-8",
		},
	});
}


/**
 * Parses the form submission from the approval dialog, extracts the state,
 * and generates Set-Cookie headers to mark the client as approved.
 *
 * @param request - The incoming POST Request object containing the form data.
 * @param cookieSecret - The secret key used to sign the approval cookie.
 * @returns A promise resolving to an object containing the parsed state and necessary headers.
 * @throws If the request method is not POST, form data is invalid, or state is missing.
 */
export async function parseRedirectApproval(
	request: Request,
	cookieSecret: string,
): Promise<ParsedApprovalResult> {
	if (request.method !== "POST") {
		throw new Error("Invalid request method. Expected POST.");
	}

	let state: any;
	let clientId: string | undefined;

	try {
		const formData = await request.formData();
		const encodedState = formData.get("state");

		if (typeof encodedState !== "string" || !encodedState) {
			throw new Error("Missing or invalid 'state' in form data.");
		}

		state = decodeState<{ oauthReqInfo?: AuthRequest }>(encodedState); // Decode the state
		clientId = state?.oauthReqInfo?.clientId; // Extract clientId from within the state

		if (!clientId) {
			throw new Error("Could not extract clientId from state object.");
		}
	} catch (e) {
		console.error("Error processing form submission:", e);
		// Rethrow or handle as appropriate, maybe return a specific error response
		throw new Error(
			`Failed to parse approval form: ${e instanceof Error ? e.message : String(e)}`,
		);
	}

	// Get existing approved clients
	const cookieHeader = request.headers.get("Cookie");
	const existingApprovedClients =
		(await getApprovedClientsFromCookie(cookieHeader, cookieSecret)) || [];

	// Add the newly approved client ID (avoid duplicates)
	const updatedApprovedClients = Array.from(new Set([...existingApprovedClients, clientId]));

	// Sign the updated list
	const payload = JSON.stringify(updatedApprovedClients);
	const key = await importKey(cookieSecret);
	const signature = await signData(key, payload);
	const newCookieValue = `${signature}.${btoa(payload)}`; // signature.base64(payload)

	// Generate Set-Cookie header
	const headers: Record<string, string> = {
		"Set-Cookie": `${COOKIE_NAME}=${newCookieValue}; HttpOnly; Secure; Path=/; SameSite=Lax; Max-Age=${ONE_YEAR_IN_SECONDS}`,
	};

	return { headers, state };
}

/**
 * Sanitizes HTML content to prevent XSS attacks
 * @param unsafe - The unsafe string that might contain HTML
 * @returns A safe string with HTML special characters escaped
 */
function sanitizeHtml(unsafe: string): string {
	return unsafe
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

// --- OAuth Helper Functions ---

/**
 * Constructs an authorization URL for an upstream service.
 *
 * @param {UpstreamAuthorizeParams} options - The parameters for constructing the URL
 * @returns {string} The authorization URL.
 */
export function getUpstreamAuthorizeUrl({
	upstream_url,
	client_id,
	scope,
	redirect_uri,
	state,
}: UpstreamAuthorizeParams): string {
	const upstream = new URL(upstream_url);
	upstream.searchParams.set("client_id", client_id);
	upstream.searchParams.set("redirect_uri", redirect_uri);
	upstream.searchParams.set("scope", scope);
	if (state) upstream.searchParams.set("state", state);
	upstream.searchParams.set("response_type", "code");
	return upstream.href;
}

/**
 * Fetches an authorization token from an upstream service.
 *
 * @param {UpstreamTokenParams} options - The parameters for the token exchange
 * @returns {Promise<[string, null] | [null, Response]>} A promise that resolves to an array containing the access token or an error response.
 */
export async function fetchUpstreamAuthToken({
	client_id,
	client_secret,
	code,
	redirect_uri,
	upstream_url,
}: UpstreamTokenParams): Promise<[string, null] | [null, Response]> {
	if (!code) {
		return [null, new Response("Missing code", { status: 400 })];
	}

	const resp = await fetch(upstream_url, {
		body: new URLSearchParams({ client_id, client_secret, code, redirect_uri }).toString(),
		headers: {
			"Content-Type": "application/x-www-form-urlencoded",
		},
		method: "POST",
	});
	if (!resp.ok) {
		console.log(await resp.text());
		return [null, new Response("Failed to fetch access token", { status: 500 })];
	}
	const body = await resp.formData();
	const accessToken = body.get("access_token") as string;
	if (!accessToken) {
		return [null, new Response("Missing access token", { status: 400 })];
	}
	return [accessToken, null];
}



================================================
FILE: src/database/connection.ts
================================================
import postgres from "postgres";

let dbInstance: postgres.Sql | null = null;

/**
 * Get database connection singleton
 * Following the pattern from BASIC-DB-MCP.md but adapted for PostgreSQL with connection pooling
 */
export function getDb(databaseUrl: string): postgres.Sql {
	if (!dbInstance) {
		dbInstance = postgres(databaseUrl, {
			// Connection pool settings for Cloudflare Workers
			max: 5, // Maximum 5 connections to fit within Workers' limit of 6 concurrent connections
			idle_timeout: 20,
			connect_timeout: 10,
			// Enable prepared statements for better performance
			prepare: true,
		});
	}
	return dbInstance;
}

/**
 * Close database connection pool
 * Call this when the Durable Object is shutting down
 */
export async function closeDb(): Promise<void> {
	if (dbInstance) {
		try {
			await dbInstance.end();
		} catch (error) {
			console.error('Error closing database connection:', error);
		} finally {
			dbInstance = null;
		}
	}
}


================================================
FILE: src/database/security.ts
================================================
import type { SqlValidationResult } from "../types";

/**
 * SQL injection protection: Basic SQL keyword validation
 * This is a simple check - in production you should use parameterized queries
 */
export function validateSqlQuery(sql: string): SqlValidationResult {
	const trimmedSql = sql.trim().toLowerCase();
	
	// Check for empty queries
	if (!trimmedSql) {
		return { isValid: false, error: "SQL query cannot be empty" };
	}
	
	// Check for obviously dangerous patterns
	const dangerousPatterns = [
		/;\s*drop\s+/i,
		/^drop\s+/i, // DROP at start of query
		/;\s*delete\s+.*\s+where\s+1\s*=\s*1/i,
		/;\s*update\s+.*\s+set\s+.*\s+where\s+1\s*=\s*1/i,
		/;\s*truncate\s+/i,
		/^truncate\s+/i, // TRUNCATE at start of query
		/;\s*alter\s+/i,
		/^alter\s+/i, // ALTER at start of query
		/;\s*create\s+/i,
		/;\s*grant\s+/i,
		/;\s*revoke\s+/i,
		/xp_cmdshell/i,
		/sp_executesql/i,
	];
	
	for (const pattern of dangerousPatterns) {
		if (pattern.test(sql)) {
			return { isValid: false, error: "Query contains potentially dangerous SQL patterns" };
		}
	}
	
	return { isValid: true };
}

/**
 * Check if a SQL query is a write operation
 */
export function isWriteOperation(sql: string): boolean {
	const trimmedSql = sql.trim().toLowerCase();
	const writeKeywords = [
		'insert', 'update', 'delete', 'create', 'drop', 'alter', 
		'truncate', 'grant', 'revoke', 'commit', 'rollback'
	];
	
	return writeKeywords.some(keyword => trimmedSql.startsWith(keyword));
}

/**
 * Format database error for user-friendly display
 */
export function formatDatabaseError(error: unknown): string {
	if (error instanceof Error) {
		// Hide sensitive connection details
		if (error.message.includes('password')) {
			return "Database authentication failed. Please check your credentials.";
		}
		if (error.message.includes('timeout')) {
			return "Database connection timed out. Please try again.";
		}
		if (error.message.includes('connection') || error.message.includes('connect')) {
			return "Unable to connect to database. Please check your connection string.";
		}
		return `Database error: ${error.message}`;
	}
	return "An unknown database error occurred.";
}


================================================
FILE: src/database/utils.ts
================================================
import postgres from "postgres";
import { getDb } from "./connection";

/**
 * Execute a database operation with proper connection management
 * Following the pattern from BASIC-DB-MCP.md but adapted for PostgreSQL
 */
export async function withDatabase<T>(
	databaseUrl: string,
	operation: (db: postgres.Sql) => Promise<T>
): Promise<T> {
	const db = getDb(databaseUrl);
	const startTime = Date.now();
	try {
		const result = await operation(db);
		const duration = Date.now() - startTime;
		console.log(`Database operation completed successfully in ${duration}ms`);
		return result;
	} catch (error) {
		const duration = Date.now() - startTime;
		console.error(`Database operation failed after ${duration}ms:`, error);
		// Re-throw the error so it can be caught by Sentry in the calling code
		throw error;
	}
	// Note: With PostgreSQL connection pooling, we don't close individual connections
	// They're returned to the pool automatically. The pool is closed when the Durable Object shuts down.
}


================================================
FILE: src/tools/database-tools-sentry.ts
================================================
import * as Sentry from "@sentry/cloudflare";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { 
	Props, 
	ListTablesSchema, 
	QueryDatabaseSchema, 
	ExecuteDatabaseSchema,
	createErrorResponse,
	createSuccessResponse
} from "../types";
import { validateSqlQuery, isWriteOperation, formatDatabaseError } from "../database/security";
import { withDatabase } from "../database/utils";

const ALLOWED_USERNAMES = new Set<string>([
	// Add GitHub usernames of users who should have access to database write operations
	// For example: 'yourusername', 'coworkerusername'
	'coleam00'
]);

// Error handling helper for MCP tools with Sentry
function handleError(error: unknown): { content: Array<{ type: "text"; text: string; isError?: boolean }> } {
	const eventId = Sentry.captureException(error);

	const errorMessage = [
		"**Error**",
		"There was a problem with your request.",
		"Please report the following to the support team:",
		`**Event ID**: ${eventId}`,
		process.env.NODE_ENV !== "production"
			? error instanceof Error
				? error.message
				: String(error)
			: "",
	].join("\n\n");

	return {
		content: [
			{
				type: "text",
				text: errorMessage,
				isError: true,
			},
		],
	};
}

export function registerDatabaseToolsWithSentry(server: McpServer, env: Env, props: Props) {
	// Tool 1: List Tables - Available to all authenticated users
	server.tool(
		"listTables",
		"Get a list of all tables in the database along with their column information. Use this first to understand the database structure before querying.",
		ListTablesSchema,
		async () => {
			return await Sentry.startNewTrace(async () => {
				return await Sentry.startSpan({
					name: "mcp.tool/listTables",
					attributes: {
						'mcp.tool.name': 'listTables',
						'mcp.user.login': props.login,
					},
				}, async (span) => {
					// Set user context
					Sentry.setUser({
						username: props.login,
						email: props.email,
					});

					try {
						return await withDatabase((env as any).DATABASE_URL, async (db) => {
							// Single query to get all table and column information (using your working query)
							const columns = await db.unsafe(`
								SELECT 
									table_name, 
									column_name, 
									data_type, 
									is_nullable,
									column_default
								FROM information_schema.columns 
								WHERE table_schema = 'public' 
								ORDER BY table_name, ordinal_position
							`);
							
							// Group columns by table
							const tableMap = new Map();
							for (const col of columns) {
								// Use snake_case property names as returned by the SQL query
								if (!tableMap.has(col.table_name)) {
									tableMap.set(col.table_name, {
										name: col.table_name,
										schema: 'public',
										columns: []
									});
								}
								tableMap.get(col.table_name).columns.push({
									name: col.column_name,
									type: col.data_type,
									nullable: col.is_nullable === 'YES',
									default: col.column_default
								});
							}
							
							const tableInfo = Array.from(tableMap.values());
							
							return {
								content: [
									{
										type: "text",
										text: `**Database Tables and Schema**\n\n${JSON.stringify(tableInfo, null, 2)}\n\n**Total tables found:** ${tableInfo.length}\n\n**Note:** Use the \`queryDatabase\` tool to run SELECT queries, or \`executeDatabase\` tool for write operations (if you have write access).`
									}
								]
							};
						});
					} catch (error) {
						console.error('listTables error:', error);
						span.setStatus({ code: 2 }); // error
						return handleError(error);
					}
				});
			});
		}
	);

	// Tool 2: Query Database - Available to all authenticated users (read-only)
	server.tool(
		"queryDatabase",
		"Execute a read-only SQL query against the PostgreSQL database. This tool only allows SELECT statements and other read operations. All authenticated users can use this tool.",
		QueryDatabaseSchema,
		async ({ sql }) => {
			return await Sentry.startNewTrace(async () => {
				return await Sentry.startSpan({
					name: "mcp.tool/queryDatabase",
					attributes: {
						'mcp.tool.name': 'queryDatabase',
						'mcp.user.login': props.login,
						'mcp.sql.query': sql.substring(0, 100), // Truncate for security
					},
				}, async (span) => {
					// Set user context
					Sentry.setUser({
						username: props.login,
						email: props.email,
					});

					try {
						// Validate the SQL query
						const validation = validateSqlQuery(sql);
						if (!validation.isValid) {
							return createErrorResponse(`Invalid SQL query: ${validation.error}`);
						}
						
						// Check if it's a write operation
						if (isWriteOperation(sql)) {
							return createErrorResponse(
								"Write operations are not allowed with this tool. Use the `executeDatabase` tool if you have write permissions (requires special GitHub username access)."
							);
						}
						
						return await withDatabase((env as any).DATABASE_URL, async (db) => {
							const results = await db.unsafe(sql);
							
							return {
								content: [
									{
										type: "text",
										text: `**Query Results**\n\`\`\`sql\n${sql}\n\`\`\`\n\n**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\`\n\n**Rows returned:** ${Array.isArray(results) ? results.length : 1}`
									}
								]
							};
						});
					} catch (error) {
						console.error('queryDatabase error:', error);
						span.setStatus({ code: 2 }); // error
						return handleError(error);
					}
				});
			});
		}
	);

	// Tool 3: Execute Database - Only available to privileged users (write operations)
	if (ALLOWED_USERNAMES.has(props.login)) {
		server.tool(
			"executeDatabase",
			"Execute any SQL statement against the PostgreSQL database, including INSERT, UPDATE, DELETE, and DDL operations. This tool is restricted to specific GitHub users and can perform write transactions. **USE WITH CAUTION** - this can modify or delete data.",
			ExecuteDatabaseSchema,
			async ({ sql }) => {
				return await Sentry.startNewTrace(async () => {
					return await Sentry.startSpan({
						name: "mcp.tool/executeDatabase",
						attributes: {
							'mcp.tool.name': 'executeDatabase',
							'mcp.user.login': props.login,
							'mcp.sql.query': sql.substring(0, 100), // Truncate for security
							'mcp.sql.is_write': isWriteOperation(sql),
						},
					}, async (span) => {
						// Set user context
						Sentry.setUser({
							username: props.login,
							email: props.email,
						});

						try {
							// Validate the SQL query
							const validation = validateSqlQuery(sql);
							if (!validation.isValid) {
								return createErrorResponse(`Invalid SQL statement: ${validation.error}`);
							}
							
							return await withDatabase((env as any).DATABASE_URL, async (db) => {
								const results = await db.unsafe(sql);
								
								const isWrite = isWriteOperation(sql);
								const operationType = isWrite ? "Write Operation" : "Read Operation";
								
								return {
									content: [
										{
											type: "text",
											text: `**${operationType} Executed Successfully**\n\`\`\`sql\n${sql}\n\`\`\`\n\n**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\`\n\n${isWrite ? '**⚠️ Database was modified**' : `**Rows returned:** ${Array.isArray(results) ? results.length : 1}`}\n\n**Executed by:** ${props.login} (${props.name})`
										}
									]
								};
							});
						} catch (error) {
							console.error('executeDatabase error:', error);
							span.setStatus({ code: 2 }); // error
							return handleError(error);
						}
					});
				});
			}
		);
	}
}


================================================
FILE: src/tools/database-tools.ts
================================================
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { 
	Props, 
	ListTablesSchema, 
	QueryDatabaseSchema, 
	ExecuteDatabaseSchema,
	createErrorResponse,
	createSuccessResponse
} from "../types";
import { validateSqlQuery, isWriteOperation, formatDatabaseError } from "../database/security";
import { withDatabase } from "../database/utils";

const ALLOWED_USERNAMES = new Set<string>([
	// Add GitHub usernames of users who should have access to database write operations
	// For example: 'yourusername', 'coworkerusername'
	'coleam00'
]);

export function registerDatabaseTools(server: McpServer, env: Env, props: Props) {
	// Tool 1: List Tables - Available to all authenticated users
	server.tool(
		"listTables",
		"Get a list of all tables in the database along with their column information. Use this first to understand the database structure before querying.",
		ListTablesSchema,
		async () => {
			try {
				return await withDatabase((env as any).DATABASE_URL, async (db) => {
					// Single query to get all table and column information (using your working query)
					const columns = await db.unsafe(`
						SELECT 
							table_name, 
							column_name, 
							data_type, 
							is_nullable,
							column_default
						FROM information_schema.columns 
						WHERE table_schema = 'public' 
						ORDER BY table_name, ordinal_position
					`);
					
					// Group columns by table
					const tableMap = new Map();
					for (const col of columns) {
						// Use snake_case property names as returned by the SQL query
						if (!tableMap.has(col.table_name)) {
							tableMap.set(col.table_name, {
								name: col.table_name,
								schema: 'public',
								columns: []
							});
						}
						tableMap.get(col.table_name).columns.push({
							name: col.column_name,
							type: col.data_type,
							nullable: col.is_nullable === 'YES',
							default: col.column_default
						});
					}
					
					const tableInfo = Array.from(tableMap.values());
					
					return {
						content: [
							{
								type: "text",
								text: `**Database Tables and Schema**\n\n${JSON.stringify(tableInfo, null, 2)}\n\n**Total tables found:** ${tableInfo.length}\n\n**Note:** Use the \`queryDatabase\` tool to run SELECT queries, or \`executeDatabase\` tool for write operations (if you have write access).`
							}
						]
					};
				});
			} catch (error) {
				console.error('listTables error:', error);
				return createErrorResponse(
					`Error retrieving database schema: ${formatDatabaseError(error)}`
				);
			}
		}
	);

	// Tool 2: Query Database - Available to all authenticated users (read-only)
	server.tool(
		"queryDatabase",
		"Execute a read-only SQL query against the PostgreSQL database. This tool only allows SELECT statements and other read operations. All authenticated users can use this tool.",
		QueryDatabaseSchema,
		async ({ sql }) => {
			try {
				// Validate the SQL query
				const validation = validateSqlQuery(sql);
				if (!validation.isValid) {
					return createErrorResponse(`Invalid SQL query: ${validation.error}`);
				}
				
				// Check if it's a write operation
				if (isWriteOperation(sql)) {
					return createErrorResponse(
						"Write operations are not allowed with this tool. Use the `executeDatabase` tool if you have write permissions (requires special GitHub username access)."
					);
				}
				
				return await withDatabase((env as any).DATABASE_URL, async (db) => {
					const results = await db.unsafe(sql);
					
					return {
						content: [
							{
								type: "text",
								text: `**Query Results**\n\`\`\`sql\n${sql}\n\`\`\`\n\n**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\`\n\n**Rows returned:** ${Array.isArray(results) ? results.length : 1}`
							}
						]
					};
				});
			} catch (error) {
				console.error('queryDatabase error:', error);
				return createErrorResponse(`Database query error: ${formatDatabaseError(error)}`);
			}
		}
	);

	// Tool 3: Execute Database - Only available to privileged users (write operations)
	if (ALLOWED_USERNAMES.has(props.login)) {
		server.tool(
			"executeDatabase",
			"Execute any SQL statement against the PostgreSQL database, including INSERT, UPDATE, DELETE, and DDL operations. This tool is restricted to specific GitHub users and can perform write transactions. **USE WITH CAUTION** - this can modify or delete data.",
			ExecuteDatabaseSchema,
			async ({ sql }) => {
				try {
					// Validate the SQL query
					const validation = validateSqlQuery(sql);
					if (!validation.isValid) {
						return createErrorResponse(`Invalid SQL statement: ${validation.error}`);
					}
					
					return await withDatabase((env as any).DATABASE_URL, async (db) => {
						const results = await db.unsafe(sql);
						
						const isWrite = isWriteOperation(sql);
						const operationType = isWrite ? "Write Operation" : "Read Operation";
						
						return {
							content: [
								{
									type: "text",
									text: `**${operationType} Executed Successfully**\n\`\`\`sql\n${sql}\n\`\`\`\n\n**Results:**\n\`\`\`json\n${JSON.stringify(results, null, 2)}\n\`\`\`\n\n${isWrite ? '**⚠️ Database was modified**' : `**Rows returned:** ${Array.isArray(results) ? results.length : 1}`}\n\n**Executed by:** ${props.login} (${props.name})`
								}
							]
						};
					});
				} catch (error) {
					console.error('executeDatabase error:', error);
					return createErrorResponse(`Database execution error: ${formatDatabaseError(error)}`);
				}
			}
		);
	}
}


================================================
FILE: src/tools/register-tools.ts
================================================
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { Props } from "../types";
import { registerDatabaseTools } from "./database-tools";

/**
 * Register all MCP tools based on user permissions
 */
export function registerAllTools(server: McpServer, env: Env, props: Props) {
	// Register database tools
	registerDatabaseTools(server, env, props);
	
	// Future tools can be registered here
	// registerOtherTools(server, env, props);
}


================================================
FILE: tests/setup.ts
================================================
import { beforeEach, vi } from 'vitest'

// Mock crypto API for Node.js environment
Object.defineProperty(global, 'crypto', {
  value: {
    subtle: {
      sign: vi.fn(),
      verify: vi.fn(),
      importKey: vi.fn(),
    },
    getRandomValues: vi.fn(),
  },
})

// Mock fetch globally
global.fetch = vi.fn()

beforeEach(() => {
  vi.clearAllMocks()
})


================================================
FILE: tests/fixtures/auth.fixtures.ts
================================================
import type { Props } from '../../src/types'

export const mockProps: Props = {
  login: 'testuser',
  name: 'Test User',
  email: 'test@example.com',
  accessToken: 'test-access-token',
}

export const mockPrivilegedProps: Props = {
  login: 'coleam00',
  name: 'Cole Medin',
  email: 'cole@example.com',
  accessToken: 'privileged-access-token',
}

export const mockGitHubUser = {
  data: {
    login: 'testuser',
    name: 'Test User',
    email: 'test@example.com',
    id: 12345,
    avatar_url: 'https://github.com/images/avatar.png',
  },
}

export const mockAuthRequest = {
  clientId: 'test-client-id',
  redirectUri: 'http://localhost:3000/callback',
  scope: 'read:user',
  state: 'test-state',
  codeChallenge: 'test-challenge',
  codeChallengeMethod: 'S256',
}

export const mockClientInfo = {
  id: 'test-client-id',
  name: 'Test Client',
  description: 'A test OAuth client',
  logoUrl: 'https://example.com/logo.png',
}

export const mockAccessToken = 'github-access-token-123'
export const mockAuthorizationCode = 'auth-code-456'
export const mockState = 'oauth-state-789'


================================================
FILE: tests/fixtures/database.fixtures.ts
================================================
export const mockTableColumns = [
  {
    table_name: 'users',
    column_name: 'id',
    data_type: 'integer',
    is_nullable: 'NO',
    column_default: 'nextval(\'users_id_seq\'::regclass)',
  },
  {
    table_name: 'users',
    column_name: 'name',
    data_type: 'character varying',
    is_nullable: 'YES',
    column_default: null,
  },
  {
    table_name: 'users',
    column_name: 'email',
    data_type: 'character varying',
    is_nullable: 'NO',
    column_default: null,
  },
  {
    table_name: 'posts',
    column_name: 'id',
    data_type: 'integer',
    is_nullable: 'NO',
    column_default: 'nextval(\'posts_id_seq\'::regclass)',
  },
  {
    table_name: 'posts',
    column_name: 'title',
    data_type: 'text',
    is_nullable: 'NO',
    column_default: null,
  },
  {
    table_name: 'posts',
    column_name: 'user_id',
    data_type: 'integer',
    is_nullable: 'NO',
    column_default: null,
  },
]

export const mockQueryResult = [
  { id: 1, name: 'John Doe', email: 'john@example.com' },
  { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
]

export const mockInsertResult = [
  { id: 3, name: 'New User', email: 'new@example.com' },
]

export const validSelectQuery = 'SELECT * FROM users WHERE id = 1'
export const validInsertQuery = 'INSERT INTO users (name, email) VALUES (\'Test\', \'test@example.com\')'
export const validUpdateQuery = 'UPDATE users SET name = \'Updated\' WHERE id = 1'
export const validDeleteQuery = 'DELETE FROM users WHERE id = 1'

export const dangerousDropQuery = 'DROP TABLE users'
export const dangerousDeleteAllQuery = 'SELECT * FROM users; DELETE FROM users WHERE 1=1'
export const maliciousInjectionQuery = 'SELECT * FROM users; DROP TABLE users; --'
export const emptyQuery = ''
export const whitespaceQuery = '   '


================================================
FILE: tests/fixtures/mcp.fixtures.ts
================================================
import type { McpResponse } from '../../src/types'

export const mockSuccessResponse: McpResponse = {
  content: [
    {
      type: 'text',
      text: '**Success**\n\nOperation completed successfully',
    },
  ],
}

export const mockErrorResponse: McpResponse = {
  content: [
    {
      type: 'text',
      text: '**Error**\n\nSomething went wrong',
      isError: true,
    },
  ],
}

export const mockQueryResponse: McpResponse = {
  content: [
    {
      type: 'text',
      text: '**Query Results**\n```sql\nSELECT * FROM users\n```\n\n**Results:**\n```json\n[\n  {\n    "id": 1,\n    "name": "John Doe"\n  }\n]\n```\n\n**Rows returned:** 1',
    },
  ],
}

export const mockTableListResponse: McpResponse = {
  content: [
    {
      type: 'text',
      text: '**Database Tables and Schema**\n\n[\n  {\n    "name": "users",\n    "schema": "public",\n    "columns": [\n      {\n        "name": "id",\n        "type": "integer",\n        "nullable": false,\n        "default": "nextval(\'users_id_seq\'::regclass)"\n      }\n    ]\n  }\n]\n\n**Total tables found:** 1\n\n**Note:** Use the `queryDatabase` tool to run SELECT queries, or `executeDatabase` tool for write operations (if you have write access).',
    },
  ],
}


================================================
FILE: tests/mocks/crypto.mock.ts
================================================
import { vi } from 'vitest'

// Mock crypto.subtle for cookie signing
export const mockCryptoSubtle = {
  sign: vi.fn(),
  verify: vi.fn(),
  importKey: vi.fn(),
}

// Mock crypto.getRandomValues
export const mockGetRandomValues = vi.fn()

export function setupCryptoMocks() {
  // Mock HMAC signing
  mockCryptoSubtle.sign.mockResolvedValue(new ArrayBuffer(32))
  
  // Mock signature verification
  mockCryptoSubtle.verify.mockResolvedValue(true)
  
  // Mock key import
  mockCryptoSubtle.importKey.mockResolvedValue({} as CryptoKey)
  
  // Mock random values
  mockGetRandomValues.mockImplementation((array: Uint8Array) => {
    for (let i = 0; i < array.length; i++) {
      array[i] = Math.floor(Math.random() * 256)
    }
    return array
  })
}

export function setupCryptoError() {
  mockCryptoSubtle.sign.mockRejectedValue(new Error('Crypto signing failed'))
  mockCryptoSubtle.verify.mockRejectedValue(new Error('Crypto verification failed'))
}

export function resetCryptoMocks() {
  vi.clearAllMocks()
  setupCryptoMocks()
}

// Apply mocks to global crypto object
if (!global.crypto) {
  Object.defineProperty(global, 'crypto', {
    value: {
      subtle: mockCryptoSubtle,
      getRandomValues: mockGetRandomValues,
    },
    writable: true,
  })
} else {
  global.crypto.subtle = mockCryptoSubtle
  global.crypto.getRandomValues = mockGetRandomValues
}


================================================
FILE: tests/mocks/database.mock.ts
================================================
import { vi } from 'vitest'
import { mockTableColumns, mockQueryResult } from '../fixtures/database.fixtures'

// Mock postgres function
export const mockPostgresInstance = {
  unsafe: vi.fn(),
  end: vi.fn(),
  // Template literal query method
  '`SELECT * FROM users`': vi.fn(),
}

// Mock the postgres module
vi.mock('postgres', () => ({
  default: vi.fn(() => mockPostgresInstance),
}))

// Mock database connection functions
vi.mock('../../src/database/connection', () => ({
  getDb: vi.fn(() => mockPostgresInstance),
  closeDb: vi.fn(),
}))

// Mock database utils
vi.mock('../../src/database/utils', () => ({
  withDatabase: vi.fn(async (url: string, operation: any) => {
    return await operation(mockPostgresInstance)
  }),
}))

// Mock setup functions
export function setupDatabaseMocks() {
  mockPostgresInstance.unsafe.mockImplementation((query: string) => {
    if (query.includes('information_schema.columns')) {
      return Promise.resolve(mockTableColumns)
    }
    if (query.includes('SELECT')) {
      return Promise.resolve(mockQueryResult)
    }
    if (query.includes('INSERT') || query.includes('UPDATE') || query.includes('DELETE')) {
      return Promise.resolve([{ affectedRows: 1 }])
    }
    return Promise.resolve([])
  })
}

export function setupDatabaseError() {
  mockPostgresInstance.unsafe.mockRejectedValue(new Error('Database connection failed'))
}

export function setupDatabaseTimeout() {
  mockPostgresInstance.unsafe.mockRejectedValue(new Error('Connection timeout'))
}

export function resetDatabaseMocks() {
  vi.clearAllMocks()
  setupDatabaseMocks()
}


================================================
FILE: tests/mocks/github.mock.ts
================================================
import { vi } from 'vitest'
import { mockGitHubUser, mockAccessToken } from '../fixtures/auth.fixtures'

// Mock Octokit
export const mockOctokit = {
  rest: {
    users: {
      getAuthenticated: vi.fn(),
    },
  },
}

vi.mock('octokit', () => ({
  Octokit: vi.fn(() => mockOctokit),
}))

// Mock GitHub API responses
export function setupGitHubMocks() {
  mockOctokit.rest.users.getAuthenticated.mockResolvedValue(mockGitHubUser)
}

export function setupGitHubError() {
  mockOctokit.rest.users.getAuthenticated.mockRejectedValue(new Error('GitHub API error'))
}

export function setupGitHubUnauthorized() {
  mockOctokit.rest.users.getAuthenticated.mockRejectedValue(new Error('Bad credentials'))
}

export function resetGitHubMocks() {
  vi.clearAllMocks()
  setupGitHubMocks()
}

// Mock fetch for GitHub OAuth token exchange
export function setupGitHubTokenExchange() {
  global.fetch = vi.fn((url: string) => {
    if (url.includes('github.com/login/oauth/access_token')) {
      return Promise.resolve({
        ok: true,
        text: () => Promise.resolve(`access_token=${mockAccessToken}&token_type=bearer&scope=read:user`),
      } as Response)
    }
    return Promise.reject(new Error('Unexpected fetch call'))
  })
}

export function setupGitHubTokenExchangeError() {
  global.fetch = vi.fn((url: string) => {
    if (url.includes('github.com/login/oauth/access_token')) {
      return Promise.resolve({
        ok: false,
        status: 400,
        text: () => Promise.resolve('error=invalid_grant&error_description=Bad verification code.'),
      } as Response)
    }
    return Promise.reject(new Error('Unexpected fetch call'))
  })
}


================================================
FILE: tests/mocks/oauth.mock.ts
================================================
import { vi } from 'vitest'
import { mockAuthRequest, mockClientInfo } from '../fixtures/auth.fixtures'

// Mock OAuth provider
export const mockOAuthProvider = {
  parseAuthRequest: vi.fn(),
  lookupClient: vi.fn(),
  completeAuthorization: vi.fn(),
}

// Mock OAuth helpers
export const mockOAuthHelpers = {
  ...mockOAuthProvider,
}

// Mock Cloudflare Workers OAuth Provider
vi.mock('@cloudflare/workers-oauth-provider', () => ({
  default: vi.fn(() => ({
    fetch: vi.fn(),
  })),
}))

export function setupOAuthMocks() {
  mockOAuthProvider.parseAuthRequest.mockResolvedValue(mockAuthRequest)
  mockOAuthProvider.lookupClient.mockResolvedValue(mockClientInfo)
  mockOAuthProvider.completeAuthorization.mockResolvedValue({
    redirectTo: 'http://localhost:3000/callback?code=success',
  })
}

export function setupOAuthError() {
  mockOAuthProvider.parseAuthRequest.mockRejectedValue(new Error('Invalid OAuth request'))
}

export function resetOAuthMocks() {
  vi.clearAllMocks()
  setupOAuthMocks()
}

// Mock environment with OAuth provider
export const mockEnv = {
  GITHUB_CLIENT_ID: 'test-client-id',
  GITHUB_CLIENT_SECRET: 'test-client-secret',
  COOKIE_ENCRYPTION_KEY: 'test-encryption-key',
  DATABASE_URL: 'postgresql://test:test@localhost:5432/test',
  OAUTH_PROVIDER: mockOAuthProvider,
}


================================================
FILE: tests/unit/database/security.test.ts
================================================
import { describe, it, expect } from 'vitest'
import { validateSqlQuery, isWriteOperation, formatDatabaseError } from '../../../src/database/security'
import {
  validSelectQuery,
  validInsertQuery,
  validUpdateQuery,
  validDeleteQuery,
  dangerousDropQuery,
  dangerousDeleteAllQuery,
  maliciousInjectionQuery,
  emptyQuery,
  whitespaceQuery,
} from '../../fixtures/database.fixtures'

describe('Database Security', () => {
  describe('validateSqlQuery', () => {
    it('should validate safe SELECT queries', () => {
      const result = validateSqlQuery(validSelectQuery)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeUndefined()
    })

    it('should validate safe INSERT queries', () => {
      const result = validateSqlQuery(validInsertQuery)
      expect(result.isValid).toBe(true)
      expect(result.error).toBeUndefined()
    })

    it('should reject empty queries', () => {
      const result = validateSqlQuery(emptyQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('SQL query cannot be empty')
    })

    it('should reject whitespace-only queries', () => {
      const result = validateSqlQuery(whitespaceQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('SQL query cannot be empty')
    })

    it('should reject dangerous DROP queries', () => {
      const result = validateSqlQuery(dangerousDropQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Query contains potentially dangerous SQL patterns')
    })

    it('should reject dangerous DELETE ALL queries', () => {
      const result = validateSqlQuery(dangerousDeleteAllQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Query contains potentially dangerous SQL patterns')
    })

    it('should reject SQL injection attempts', () => {
      const result = validateSqlQuery(maliciousInjectionQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Query contains potentially dangerous SQL patterns')
    })

    it('should handle case-insensitive dangerous patterns', () => {
      const upperCaseQuery = 'SELECT * FROM users; DROP TABLE users;'
      const result = validateSqlQuery(upperCaseQuery)
      expect(result.isValid).toBe(false)
      expect(result.error).toBe('Query contains potentially dangerous SQL patterns')
    })
  })

  describe('isWriteOperation', () => {
    it('should identify SELECT as read operation', () => {
      expect(isWriteOperation(validSelectQuery)).toBe(false)
    })

    it('should identify INSERT as write operation', () => {
      expect(isWriteOperation(validInsertQuery)).toBe(true)
    })

    it('should identify UPDATE as write operation', () => {
      expect(isWriteOperation(validUpdateQuery)).toBe(true)
    })

    it('should identify DELETE as write operation', () => {
      expect(isWriteOperation(validDeleteQuery)).toBe(true)
    })

    it('should identify DROP as write operation', () => {
      expect(isWriteOperation(dangerousDropQuery)).toBe(true)
    })

    it('should handle case-insensitive operations', () => {
      expect(isWriteOperation('insert into users values (1, \'test\')')).toBe(true)
      expect(isWriteOperation('UPDATE users SET name = \'test\'')).toBe(true)
      expect(isWriteOperation('Delete from users where id = 1')).toBe(true)
    })

    it('should handle queries with leading whitespace', () => {
      expect(isWriteOperation('   INSERT INTO users VALUES (1, \'test\')')).toBe(true)
      expect(isWriteOperation('\t\nSELECT * FROM users')).toBe(false)
    })
  })

  describe('formatDatabaseError', () => {
    it('should format generic database errors', () => {
      const error = new Error('Connection failed')
      const result = formatDatabaseError(error)
      expect(result).toBe('Database error: Connection failed')
    })

    it('should sanitize password errors', () => {
      const error = new Error('authentication failed for user "test" with password "secret123"')
      const result = formatDatabaseError(error)
      expect(result).toBe('Database authentication failed. Please check your credentials.')
    })

    it('should handle timeout errors', () => {
      const error = new Error('Connection timeout after 30 seconds')
      const result = formatDatabaseError(error)
      expect(result).toBe('Database connection timed out. Please try again.')
    })

    it('should handle connection errors', () => {
      const error = new Error('Could not connect to database server')
      const result = formatDatabaseError(error)
      expect(result).toBe('Unable to connect to database. Please check your connection string.')
    })

    it('should handle non-Error objects', () => {
      const result = formatDatabaseError('string error')
      expect(result).toBe('An unknown database error occurred.')
    })

    it('should handle null/undefined errors', () => {
      expect(formatDatabaseError(null)).toBe('An unknown database error occurred.')
      expect(formatDatabaseError(undefined)).toBe('An unknown database error occurred.')
    })
  })
})


================================================
FILE: tests/unit/database/utils.test.ts
================================================
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the database connection module
const mockDbInstance = {
  unsafe: vi.fn(),
  end: vi.fn(),
}

vi.mock('../../../src/database/connection', () => ({
  getDb: vi.fn(() => mockDbInstance),
}))

// Now import the modules
import { withDatabase } from '../../../src/database/utils'

describe('Database Utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('withDatabase', () => {
    it('should execute database operation successfully', async () => {
      const mockOperation = vi.fn().mockResolvedValue('success')
      const result = await withDatabase('test-url', mockOperation)
      
      expect(result).toBe('success')
      expect(mockOperation).toHaveBeenCalledWith(mockDbInstance)
    })

    it('should handle database operation errors', async () => {
      const mockOperation = vi.fn().mockRejectedValue(new Error('Operation failed'))
      
      await expect(withDatabase('test-url', mockOperation)).rejects.toThrow('Operation failed')
      expect(mockOperation).toHaveBeenCalledWith(mockDbInstance)
    })

    it('should log successful operations', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const mockOperation = vi.fn().mockResolvedValue('success')
      
      await withDatabase('test-url', mockOperation)
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringMatching(/Database operation completed successfully in \d+ms/)
      )
      consoleSpy.mockRestore()
    })

    it('should log failed operations', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const mockOperation = vi.fn().mockRejectedValue(new Error('Operation failed'))
      
      await expect(withDatabase('test-url', mockOperation)).rejects.toThrow('Operation failed')
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringMatching(/Database operation failed after \d+ms:/),
        expect.any(Error)
      )
      consoleSpy.mockRestore()
    })

    it('should measure execution time', async () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const mockOperation = vi.fn().mockImplementation(async () => {
        // Simulate some delay
        await new Promise(resolve => setTimeout(resolve, 10))
        return 'success'
      })
      
      await withDatabase('test-url', mockOperation)
      
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringMatching(/Database operation completed successfully in \d+ms/)
      )
      consoleSpy.mockRestore()
    })
  })
})


================================================
FILE: tests/unit/tools/database-tools.test.ts
================================================
import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock the database modules
const mockDbInstance = {
  unsafe: vi.fn(),
  end: vi.fn(),
}

vi.mock('../../../src/database/connection', () => ({
  getDb: vi.fn(() => mockDbInstance),
}))

vi.mock('../../../src/database/utils', () => ({
  withDatabase: vi.fn(async (url: string, operation: any) => {
    return await operation(mockDbInstance)
  }),
}))

// Now import the modules
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { registerDatabaseTools } from '../../../src/tools/database-tools'
import { mockProps, mockPrivilegedProps } from '../../fixtures/auth.fixtures'
import { mockEnv } from '../../mocks/oauth.mock'
import { mockTableColumns, mockQueryResult } from '../../fixtures/database.fixtures'

describe('Database Tools', () => {
  let mockServer: McpServer
  
  beforeEach(() => {
    vi.clearAllMocks()
    mockServer = new McpServer({ name: 'test', version: '1.0.0' })
    
    // Setup database mocks
    mockDbInstance.unsafe.mockImplementation((query: string) => {
      if (query.includes('information_schema.columns')) {
        return Promise.resolve(mockTableColumns)
      }
      if (query.includes('SELECT')) {
        return Promise.resolve(mockQueryResult)
      }
      if (query.includes('INSERT') || query.includes('UPDATE') || query.includes('DELETE')) {
        return Promise.resolve([{ affectedRows: 1 }])
      }
      return Promise.resolve([])
    })
  })

  describe('registerDatabaseTools', () => {
    it('should register listTables and queryDatabase for regular users', () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      expect(toolSpy).toHaveBeenCalledWith(
        'listTables',
        expect.any(String),
        expect.any(Object),
        expect.any(Function)
      )
      expect(toolSpy).toHaveBeenCalledWith(
        'queryDatabase',
        expect.any(String),
        expect.any(Object),
        expect.any(Function)
      )
      expect(toolSpy).toHaveBeenCalledTimes(2)
    })

    it('should register all tools for privileged users', () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      
      registerDatabaseTools(mockServer, mockEnv as any, mockPrivilegedProps)
      
      expect(toolSpy).toHaveBeenCalledWith(
        'listTables',
        expect.any(String),
        expect.any(Object),
        expect.any(Function)
      )
      expect(toolSpy).toHaveBeenCalledWith(
        'queryDatabase',
        expect.any(String),
        expect.any(Object),
        expect.any(Function)
      )
      expect(toolSpy).toHaveBeenCalledWith(
        'executeDatabase',
        expect.any(String),
        expect.any(Object),
        expect.any(Function)
      )
      expect(toolSpy).toHaveBeenCalledTimes(3)
    })
  })

  describe('listTables tool', () => {
    it('should return table schema successfully', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      // Get the registered tool handler
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'listTables')
      const handler = toolCall![3] as Function
      
      const result = await handler({})
      
      expect(result.content).toBeDefined()
      expect(result.content[0].type).toBe('text')
      expect(result.content[0].text).toContain('Database Tables and Schema')
      expect(result.content[0].text).toContain('users')
      expect(result.content[0].text).toContain('posts')
    })

    it('should handle database errors', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      mockDbInstance.unsafe.mockRejectedValue(new Error('Database connection failed'))
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'listTables')
      const handler = toolCall![3] as Function
      
      const result = await handler({})
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Error')
    })
  })

  describe('queryDatabase tool', () => {
    it('should execute SELECT queries successfully', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'queryDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'SELECT * FROM users' })
      
      expect(result.content[0].type).toBe('text')
      expect(result.content[0].text).toContain('Query Results')
      expect(result.content[0].text).toContain('SELECT * FROM users')
    })

    it('should reject write operations', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'queryDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'INSERT INTO users VALUES (1, \'test\')' })
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Write operations are not allowed')
    })

    it('should reject invalid SQL', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'queryDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'SELECT * FROM users; DROP TABLE users' })
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Invalid SQL query')
    })

    it('should handle database errors', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      mockDbInstance.unsafe.mockRejectedValue(new Error('Database connection failed'))
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'queryDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'SELECT * FROM users' })
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Database query error')
    })
  })

  describe('executeDatabase tool', () => {
    it('should only be available to privileged users', async () => {
      // Regular user should not get executeDatabase
      const toolSpy1 = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockProps)
      
      const executeToolCall = toolSpy1.mock.calls.find(call => call[0] === 'executeDatabase')
      expect(executeToolCall).toBeUndefined()
      
      // Privileged user should get executeDatabase
      const mockServer2 = new McpServer({ name: 'test2', version: '1.0.0' })
      const toolSpy2 = vi.spyOn(mockServer2, 'tool')
      registerDatabaseTools(mockServer2, mockEnv as any, mockPrivilegedProps)
      
      const privilegedExecuteToolCall = toolSpy2.mock.calls.find(call => call[0] === 'executeDatabase')
      expect(privilegedExecuteToolCall).toBeDefined()
    })

    it('should execute write operations for privileged users', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockPrivilegedProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'executeDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'INSERT INTO users VALUES (1, \'test\')' })
      
      expect(result.content[0].type).toBe('text')
      expect(result.content[0].text).toContain('Write Operation Executed Successfully')
      expect(result.content[0].text).toContain('coleam00')
    })

    it('should execute read operations for privileged users', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockPrivilegedProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'executeDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'SELECT * FROM users' })
      
      expect(result.content[0].type).toBe('text')
      expect(result.content[0].text).toContain('Read Operation Executed Successfully')
    })

    it('should reject invalid SQL', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      registerDatabaseTools(mockServer, mockEnv as any, mockPrivilegedProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'executeDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'SELECT * FROM users; DROP TABLE users' })
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Invalid SQL statement')
    })

    it('should handle database errors', async () => {
      const toolSpy = vi.spyOn(mockServer, 'tool')
      mockDbInstance.unsafe.mockRejectedValue(new Error('Database connection failed'))
      registerDatabaseTools(mockServer, mockEnv as any, mockPrivilegedProps)
      
      const toolCall = toolSpy.mock.calls.find(call => call[0] === 'executeDatabase')
      const handler = toolCall![3] as Function
      
      const result = await handler({ sql: 'INSERT INTO users VALUES (1, \'test\')' })
      
      expect(result.content[0].isError).toBe(true)
      expect(result.content[0].text).toContain('Database execution error')
    })
  })
})


================================================
FILE: tests/unit/utils/response-helpers.test.ts
================================================
import { describe, it, expect } from 'vitest'
import { createSuccessResponse, createErrorResponse } from '../../../src/types'

describe('Response Helpers', () => {
  describe('createSuccessResponse', () => {
    it('should create success response with message only', () => {
      const response = createSuccessResponse('Operation completed')
      
      expect(response.content).toHaveLength(1)
      expect(response.content[0].type).toBe('text')
      expect(response.content[0].text).toBe('**Success**\n\nOperation completed')
      expect(response.content[0].isError).toBeUndefined()
    })

    it('should create success response with message and data', () => {
      const data = { id: 1, name: 'Test' }
      const response = createSuccessResponse('User created', data)
      
      expect(response.content).toHaveLength(1)
      expect(response.content[0].type).toBe('text')
      expect(response.content[0].text).toContain('**Success**')
      expect(response.content[0].text).toContain('User created')
      expect(response.content[0].text).toContain('**Result:**')
      expect(response.content[0].text).toContain(JSON.stringify(data, null, 2))
    })

    it('should handle null data', () => {
      const response = createSuccessResponse('Operation completed', null)
      
      expect(response.content[0].text).toContain('**Success**')
      expect(response.content[0].text).toContain('Operation completed')
      expect(response.content[0].text).toContain('**Result:**')
      expect(response.content[0].text).toContain('null')
    })

    it('should handle undefined data', () => {
      const response = createSuccessResponse('Operation completed', undefined)
      
      expect(response.content[0].text).toBe('**Success**\n\nOperation completed')
      expect(response.content[0].text).not.toContain('**Result:**')
    })

    it('should handle complex data objects', () => {
      const data = {
        users: [
          { id: 1, name: 'Alice' },
          { id: 2, name: 'Bob' }
        ],
        meta: {
          total: 2,
          page: 1
        }
      }
      
      const response = createSuccessResponse('Users retrieved', data)
      
      expect(response.content[0].text).toContain('**Success**')
      expect(response.content[0].text).toContain('Users retrieved')
      expect(response.content[0].text).toContain('Alice')
      expect(response.content[0].text).toContain('Bob')
      expect(response.content[0].text).toContain('total')
    })
  })

  describe('createErrorResponse', () => {
    it('should create error response with message only', () => {
      const response = createErrorResponse('Something went wrong')
      
      expect(response.content).toHaveLength(1)
      expect(response.content[0].type).toBe('text')
      expect(response.content[0].text).toBe('**Error**\n\nSomething went wrong')
      expect(response.content[0].isError).toBe(true)
    })

    it('should create error response with message and details', () => {
      const details = { code: 'VALIDATION_ERROR', field: 'email' }
      const response = createErrorResponse('Validation failed', details)
      
      expect(response.content).toHaveLength(1)
      expect(response.content[0].type).toBe('text')
      expect(response.content[0].text).toContain('**Error**')
      expect(response.content[0].text).toContain('Validation failed')
      expect(response.content[0].text).toContain('**Details:**')
      expect(response.content[0].text).toContain(JSON.stringify(details, null, 2))
      expect(response.content[0].isError).toBe(true)
    })

    it('should handle null details', () => {
      const response = createErrorResponse('Operation failed', null)
      
      expect(response.content[0].text).toContain('**Error**')
      expect(response.content[0].text).toContain('Operation failed')
      expect(response.content[0].text).toContain('**Details:**')
      expect(response.content[0].text).toContain('null')
    })

    it('should handle undefined details', () => {
      const response = createErrorResponse('Operation failed', undefined)
      
      expect(response.content[0].text).toBe('**Error**\n\nOperation failed')
      expect(response.content[0].text).not.toContain('**Details:**')
    })

    it('should handle error objects as details', () => {
      const error = new Error('Database connection failed')
      const response = createErrorResponse('Database error', error)
      
      expect(response.content[0].text).toContain('**Error**')
      expect(response.content[0].text).toContain('Database error')
      expect(response.content[0].text).toContain('**Details:**')
      expect(response.content[0].isError).toBe(true)
    })

    it('should handle complex error details', () => {
      const details = {
        error: 'AUTHENTICATION_FAILED',
        message: 'Invalid credentials',
        attempts: 3,
        nextRetryAt: new Date().toISOString()
      }
      
      const response = createErrorResponse('Authentication failed', details)
      
      expect(response.content[0].text).toContain('AUTHENTICATION_FAILED')
      expect(response.content[0].text).toContain('Invalid credentials')
      expect(response.content[0].text).toContain('attempts')
      expect(response.content[0].isError).toBe(true)
    })
  })

  describe('response format consistency', () => {
    it('should maintain consistent structure across response types', () => {
      const successResponse = createSuccessResponse('Success message')
      const errorResponse = createErrorResponse('Error message')
      
      // Both should have the same structure
      expect(successResponse.content).toHaveLength(1)
      expect(errorResponse.content).toHaveLength(1)
      
      expect(successResponse.content[0].type).toBe('text')
      expect(errorResponse.content[0].type).toBe('text')
      
      expect(typeof successResponse.content[0].text).toBe('string')
      expect(typeof errorResponse.content[0].text).toBe('string')
    })

    it('should distinguish between success and error responses', () => {
      const successResponse = createSuccessResponse('Success message')
      const errorResponse = createErrorResponse('Error message')
      
      expect(successResponse.content[0].isError).toBeUndefined()
      expect(errorResponse.content[0].isError).toBe(true)
    })
  })
})


================================================
FILE: .claude/settings.local.json
================================================
{
  "permissions": {
    "allow": [
      "Bash(mkdir:*)",
      "Bash(mv:*)",
      "Bash(npm run type-check:*)",
      "Bash(npx tsc:*)",
      "Bash(npm test)"
    ],
    "deny": []
  }
}


================================================
FILE: .claude/commands/prp-mcp-create.md
================================================
---
name: "prp-mcp-create"
description: This command is designed to create a comprehensive Product Requirement Prompt (PRP) for building Model Context Protocol (MCP) servers referencing this codebase patterns mirroring tool setups for the users specific requirements.
Usage: /prp-mcp-create path/to/prp.md
Example usage: /prp-mcp-create weather-server "MCP server for weather data with API integration"
Example usage: /prp-mcp-create file-manager "MCP server mirroring task master mcp"
```
---

# Create MCP Server PRP

Create a comprehensive Product Requirement Prompt (PRP) for building Model Context Protocol (MCP) servers with authentication, database integration, and Cloudflare Workers deployment.

Before you start ensure that you read these key files to get an understanding about the goal of the PRP:
PRPs/README.md
PRPs/templates/prp_cp_base.md

## Users MCP use case: $ARGUMENTS

## Purpose

Generate context-rich PRPs specifically designed for MCP server development, using the proven patterns in this codebase that is a scaffolding of a MCP server setup that the user can build upon, including GitHub OAuth, and production-ready Cloudflare Workers deployment.

None of the existing tools will likely be reused and the tools should be created for the users use case specifically tailored to their needs.

## Execution Process

1. **Research & Context Gathering**
   - Create clear todos and spawn subagents to search the codebase for similar features/patterns Think hard and plan your approach
   - Gather relevant documentation about MCP tools, resources, and authentication flows
   - Research existing tool patterns to understand how to build the users specified use case
   - Study existing integration patterns in the codebase

2. **Generate Comprehensive PRP**
   - Use the specialized `PRPs/templates/prp_mcp_base.md` template as the foundation
   - Customize the template with specific server requirements and functionality
   - Include all necessary context from the codebase patterns and ai_docs
   - Add specific validation loops for MCP server development
   - Include database integration patterns and security considerations

3. **Enhance with AI docs**
   - The use might have added docs in PRPs/ai_docs/ directory that you should read
   - If there are docs in the PRPs/ai_docs/ directory, review them and take them into context as you build the PRP

## Implementation Details

### PRP Structure for MCP Servers

The generated PRP uses the specialized template `PRPs/templates/prp_mcp_base.md` and includes:

- **Goal**: Clear description of the MCP server to be built with authentication and database integration
- **Context**: All necessary documentation including PRPs/ai_docs/ references and existing codebase patterns
- **Implementation Blueprint**: Step-by-step TypeScript tasks following Cloudflare Workers patterns
- **Validation Loop**: Comprehensive MCP-specific testing from compilation to production deployment
- **Security Considerations**: GitHub OAuth flows, database access patterns, and SQL injection protection

### Key Features

- **Context-Rich**: Includes all patterns and references using relative paths from this proven codebase
- **Validation-Driven**: Multi-level validation from syntax to production deployment
- **Security-First**: Built-in authentication and authorization patterns
- **Production-Ready**: Cloudflare Workers deployment and monitoring

### Research Areas

1. **MCP Protocol Patterns**
   - Tool registration and validation
   - Resource serving and caching
   - Error handling and logging
   - Client communication patterns

2. **Authentication Integration**
   - GitHub OAuth implementation
   - User permission systems
   - Token management and validation
   - Session handling patterns

## Output

Creates a comprehensive PRP file in the PRPs/ directory with:

- All necessary context and code patterns
- Step-by-step implementation tasks
- Validation loops for MCP server development

## Validation

The command ensures:

- All referenced code patterns exist in the codebase
- Documentation links are valid and accessible
- Implementation tasks are specific and actionable
- Validation loops are comprehensive and executable by claude code (IMPORTANT)

## Integration with Existing Patterns

- Uses specialized MCP template from `PRPs/templates/prp_mcp_base.md`
- Follows the established directory structure and naming conventions
- Integrates with existing validation patterns and tools
- Leverages proven patterns from the current MCP server implementation in `src/`



## Notes

- Generated PRPs are immediately executable with the companion `/prp-mcp-execute` command
- All patterns are based on the proven implementation in this codebase
- Includes comprehensive error handling and recovery patterns
- Optimized for Claude Code's TodoWrite tool usage and validation loops



================================================
FILE: .claude/commands/prp-mcp-execute.md
================================================
---
name: "prp-mcp-execute"
description: This command is designed to create a comprehensive Model Context Protocol (MCP) servers following the specific Product Requirement Prompt (PRP) passed as an argument, referencing this codebase patterns mirroring tool setups for the users specific requirements.
Usage: /prp-mcp-execute path/to/prp.md
---

# Execute MCP Server PRP

Execute a comprehensive Product Requirement Prompt (PRP) for building Model Context Protocol (MCP) servers with authentication, database integration, and Cloudflare Workers deployment.

PRP to execute: $ARGUMENTS

## Purpose

Execute MCP server PRPs with comprehensive validation, testing, and deployment verification following the proven patterns from this codebase.

## Execution Process

1. **Load & Analyze PRP**
   - Read the specified PRP file completely
   - Understand all context, requirements, and validation criteria
   - Create comprehensive todo list using TodoWrite tool
   - Identify all dependencies and integration points

2. **Context Gathering & Research**
   - Use Task agents to research existing MCP server patterns
   - Study authentication flows and database integration patterns
   - Research Cloudflare Workers deployment and environment setup
   - Gather all necessary documentation and code examples

3. **Implementation Phase**
   - Execute all implementation tasks in the correct order
   - Follow TypeScript patterns from the existing codebase
   - Implement MCP tools, resources, and authentication flows
   - Add comprehensive error handling and logging

## Notes

- Uses TodoWrite tool for comprehensive task management
- Follows all patterns from the proven codebase implementation
- Includes comprehensive error handling and recovery
- Optimized for Claude Code's validation loops
- Production-ready with monitoring and logging
- Compatible with MCP Inspector and Claude Desktop


