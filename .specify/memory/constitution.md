<!--
Sync Impact Report:
- Version change: 1.0.0 → 1.0.0 (no version increment as this is the initial version based on user input)
- Modified principles: [PRINCIPLE_1_NAME] → Academic Rigor, [PRINCIPLE_2_NAME] → Technical Excellence, [PRINCIPLE_3_NAME] → User-Centered Design
- Added sections: Academic Writing Standards, Technical Standards, Performance Standards, Technical Constraints, Content Constraints, Feature Constraints, Success Criteria, Decision-Making Framework, Code Review Checklist, Documentation Requirements, Version Control Standards, Quality Gates, Ethical Guidelines, Escalation Path
- Removed sections: None (completely new constitution)
- Templates requiring updates:
  - .specify/templates/plan-template.md ✅ updated
  - .specify/templates/spec-template.md ✅ updated
  - .specify/templates/tasks-template.md ✅ updated
  - .specify/templates/commands/*.md ⚠ pending
- Follow-up TODOs: None
-->

# AI-Native Software Development Research Book with Integrated RAG Chatbot Constitution

## Core Principles

### Academic Rigor
- Accuracy through primary source verification
- All factual claims must be traceable and reproducible
- Prefer peer-reviewed sources (minimum 50% of all citations)
- Zero tolerance for plagiarism or unverified claims

### Technical Excellence
- Production-ready, maintainable code
- Comprehensive error handling and logging
- Security-first approach (authentication, data privacy)
- Performance optimization (caching, async operations)
- Accessibility compliance (WCAG 2.1 AA minimum)

### User-Centered Design
- Clear, intuitive interfaces
- Responsive design (mobile-first)
- Progressive enhancement
- Graceful degradation for feature failures

## Key Standards

### Academic Writing Standards
- **Citation Format**: APA style (7th edition)
- **Source Types**: Minimum 50% peer-reviewed articles from academic journals
- **Plagiarism**: 0% tolerance - all content must be original or properly quoted and cited
- **Writing Clarity**: Flesch-Kincaid readability grade 10-12
- **Word Count**: 5,000-7,000 words total (distributed across chapters)
- **Minimum Sources**: 15 authoritative sources across entire book
- **Fact-Checking**: Every claim verified against primary sources before publication

### Technical Standards
- **Code Quality**:
  - Type hints/TypeScript strict mode enforced
  - Unit test coverage >80% for critical paths
  - ESLint/Pylint with zero errors
  - Code review checklist passed

- **API Design**:
  - RESTful conventions
  - Proper HTTP status codes
  - Rate limiting implemented
  - API documentation auto-generated (OpenAPI/Swagger)

- **Database**:
  - Proper indexing for query performance
  - Migration scripts for schema changes
  - Backup strategy documented
  - Connection pooling configured

- **Security**:
  - Environment variables for secrets (never hardcoded)
  - HTTPS only in production
  - Input validation and sanitization
  - SQL injection prevention (parameterized queries)
  - CORS properly configured

### Performance Standards
- **Page Load**: <3 seconds on 3G connection
- **API Response**: <500ms for 95th percentile
- **Chatbot Response**: <5 seconds for RAG queries
- **Embedding Generation**: Batch processing for efficiency
- **Caching**: Redis/in-memory for frequently accessed content

## Constraints

### Technical Constraints
- **Frontend**: Docusaurus v3, React 18+, TypeScript
- **Backend**: FastAPI (Python 3.11+), async/await required
- **Database**: Neon Serverless Postgres only
- **Vector DB**: Qdrant Cloud Free Tier only (1GB limit)
- **LLM**: OpenAI Agents/ChatKit SDKs only
- **Authentication**: Better Auth (https://www.better-auth.com/) only
- **Hosting**: GitHub Pages for frontend, suggest Vercel/Railway/Render for backend
- **Budget**: Free tier services only (no paid plans)

### Content Constraints
- **Language**: Primary English, optional Urdu translation
- **Audience**: Computer science academics and professionals
- **Scope**: AI-native software development only
- **Format**: Multi-chapter book structure in MDX
- **Media**: Code examples, diagrams (Mermaid), and academic citations only

### Feature Constraints
- **Base Features (Required for 100 points)**:
  1. Docusaurus book deployed to GitHub Pages
  2. RAG chatbot answering book content questions
  3. Selected text query capability ("Ask about this selection")

- **Bonus Features (Optional, 50 points each)**:
  1. Claude Code Subagents and Agent Skills
  2. Better Auth signup/signin with user profiling
  3. Content personalization based on user background
  4. Urdu translation with RTL support

## Success Criteria

### Academic Success Criteria
✓ All claims verified against authoritative sources
✓ Zero plagiarism detected (Turnitin or similar)
✓ Passes peer fact-checking review
✓ APA citation format 100% correct
✓ Readability score within target range (FK 10-12)
✓ Minimum source count met (15+ sources)
✓ 50%+ citations from peer-reviewed journals

### Technical Success Criteria
✓ All tests passing (unit + integration)
✓ Zero critical security vulnerabilities (npm audit / safety)
✓ Lighthouse score >90 (performance, accessibility, SEO)
✓ API documentation complete and accurate
✓ Error handling covers all edge cases
✓ Mobile responsive on iOS and Android
✓ Cross-browser compatible (Chrome, Firefox, Safari, Edge)

### Functional Success Criteria
✓ RAG chatbot accurately answers book questions (>85% user satisfaction)
✓ Selected text queries return relevant responses
✓ Personalization adapts content to user level (if implemented)
✓ Translation maintains technical accuracy (if implemented)
✓ Authentication flow works without errors (if implemented)
✓ No data loss or corruption during operations

### User Experience Success Criteria
✓ Chatbot responds within 5 seconds
✓ UI is intuitive (usability test with 5+ users)
✓ Clear error messages guide user recovery
✓ Loading states inform users of progress
✓ Accessibility tested with screen reader

## Governance

### Decision-Making Framework
When faced with trade-offs, prioritize in this order:
1. **Academic Integrity** - Never compromise on source accuracy or plagiarism
2. **User Safety/Privacy** - Protect user data, secure authentication
3. **Core Functionality** - Base features must work flawlessly
4. **Performance** - Fast load times and responses
5. **Bonus Features** - Add only if base is solid

### Code Review Checklist
Before committing code, verify:
- [ ] Follows project file structure
- [ ] No hardcoded secrets or API keys
- [ ] Error handling implemented
- [ ] Tests written and passing
- [ ] Comments on complex logic
- [ ] No console.log/print debug statements
- [ ] Linting passes with zero errors
- [ ] Academic content cited properly (if applicable)

### Documentation Requirements
Every module/component must include:
- Purpose and responsibilities
- Input/output specifications
- Dependencies
- Usage examples
- Error handling behavior
- Performance considerations

### Version Control Standards
- **Commit Messages**: Conventional Commits format (feat:, fix:, docs:, etc.)
- **Branch Strategy**: main (production), develop (integration), feature/* (new features)
- **Pull Requests**: Required for all changes, include description and testing notes
- **CI/CD**: GitHub Actions for automated testing and deployment

## Quality Gates

### Pre-Commit
- Linting passes
- Type checking passes
- Local tests pass

### Pre-Merge
- All tests pass in CI
- Code review approved
- Documentation updated
- No merge conflicts

### Pre-Deployment
- Staging environment tested
- Performance benchmarks met
- Security scan clean
- Accessibility audit passed

## Ethical Guidelines

1. **Transparency**: Clearly indicate AI-generated content vs. human-written
2. **Attribution**: Credit all sources properly, respect intellectual property
3. **Privacy**: User data minimization, explicit consent for data collection
4. **Bias Awareness**: Review AI responses for potential biases, provide balanced perspectives
5. **Accessibility**: Ensure content is accessible to users with disabilities

## Escalation Path

When encountering issues:
1. **Minor Issues**: Document in code comments, create TODO
2. **Blocking Issues**: Flag immediately, suggest alternatives
3. **Scope Changes**: Request clarification before proceeding
4. **Security Concerns**: Halt development, report immediately
5. **Academic Integrity Questions**: Default to most conservative interpretation

---

**Version**: 1.0
**Ratified**: 2025-12-08
**Last Amended**: 2025-12-08

This constitution governs all code, content, and architectural decisions for this project.
