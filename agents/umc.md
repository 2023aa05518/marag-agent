# GitHub Copilot Development Guidelines

## ### 💬 Code Comments
- **Keep only minimum required comments, do not generate comments for each line**
- Comment the "why" not the "what" - let code be self-documenting
- Focus comments on business logic, algorithms, and non-obvious decisions
- Avoid redundant comments that restate what the code obviously does

### 📝 Communication Style
- **Do not use too much jargon, only use most appropriate technical terms**
- Keep explanations technical but easy to read with clear narrative flow
- Try to use simple paragraphs that build understanding progressively
- Favor plain English over complex terminology when meaning is preserved

### 📚 Consult Official Documentationinciples

### 🔒 Explicit Change Requests Only
- **Don't modify code automatically unless explicitly asked**
- Wait for clear permission before using file editing tools
- Provide suggestions in markdown code blocks for review first

### 📋 High-Level Plan First
- **Provide a 200-word summary outlining approach**
- Explain the overall strategy before diving into implementation
- Include reasoning for chosen approach

### 🎯 Scope of Impact
- **List all files/components affected**
- Identify dependencies and integration points
- Highlight potential breaking changes

### 🏗️ Architecture Overview
- **Diagram or describe how the change fits into existing design**
- Show relationships with current components
- Explain how new code integrates with existing patterns

## Development Standards

### 📁 Minimal File Creation
- **Only generate new files if strictly necessary**
- Prefer extending existing files when possible
- Justify new file creation with clear reasoning

### ⚖️ Option Evaluation
- **Present implementation options, mark your recommended choice**
- Compare pros/cons of different approaches
- Clearly indicate preferred solution with reasoning

### ♻️ Leverage Existing Assets
- **Reuse code snippets and libraries already in the project**
- Check existing utilities before creating new ones
- Follow established patterns and conventions

### 📖 Keep Code Minimal and Readable
- **Write only what's required, favor clarity over cleverness**
- Use descriptive variable and function names
- Include necessary comments for complex logic

### � Code Comments
- **Keep only minimum required comments, do not generate comments for each line**
- Comment the "why" not the "what" - let code be self-documenting
- Focus comments on business logic, algorithms, and non-obvious decisions
- Avoid redundant comments that restate what the code obviously does

### �📚 Consult Official Documentation
- **Reference the project's pyproject.toml and each library's documentation**
- Use recommended patterns from official sources
- Stay current with library best practices

### 🔍 Use Pydantic for Schemas
- **Apply Pydantic models wherever structured data validation is needed**
- Leverage existing schema patterns in the project
- Ensure type safety and validation consistency

## Workflow Protocol

1. **Analyze Request** - Understand requirements and constraints
2. **Plan Approach** - 200-word summary with architecture considerations
3. **Identify Impact** - List all affected files and components
4. **Present Options** - Show alternatives with recommendation
5. **Wait for Approval** - Get explicit permission before implementation
6. **Implement Carefully** - Make precise, minimal changes

---
*These guidelines ensure consistent, thoughtful development practices for this multi-agent RAG system.*
