# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-29

### Added
- ✅ FastAPI backend with comprehensive endpoints
- ✅ Streamlit web interface for resume upload and analysis
- ✅ Machine learning model for resume classification
- ✅ Hugging Face integration for AI-powered summarization
- ✅ Resume scoring algorithm based on keywords and alignment
- ✅ Skills and strengths extraction
- ✅ Role recommendations engine
- ✅ SQLite database for persistent storage
- ✅ API key-based authentication
- ✅ CORS middleware for cross-origin requests
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ GitHub Codespaces configuration
- ✅ Comprehensive test suite (12 tests)
- ✅ PDF text extraction with pypdf
- ✅ Text preprocessing and cleaning
- ✅ Comprehensive documentation
- ✅ MIT License

### Features
- Resume classification into 4 categories: Tech, Finance, Healthcare, Education
- Fast classification endpoint (~200ms)
- Full analysis with AI integration (~500ms)
- Skill detection from resume text
- Strength identification using keyword matching
- Confidence scoring system (0-100)
- Suggested job roles based on category
- Summary generation using BART model
- Database persistence with SQLite
- User-friendly Streamlit UI

### Security
- API key authentication on all endpoints
- Input validation on file uploads
- PDF file type enforcement
- Non-root Docker user
- Environment-based secrets
- CORS configuration

### Performance
- Multi-stage Docker build
- Layer caching optimization
- Efficient text processing
- Concurrent request handling

## [0.1.0] - 2026-05-25

### Initial Release
- Basic project structure
- Training data setup
- Initial ML model training
- Pytest configuration

---

## Planned Features

### v1.1.0
- [ ] Batch resume processing
- [ ] Export analysis results (PDF, CSV)
- [ ] Advanced filtering in history
- [ ] Resume templates analysis
- [ ] Salary range predictions
- [ ] Skills gap analysis

### v1.2.0
- [ ] Multi-language support
- [ ] Custom classification categories
- [ ] User accounts and dashboards
- [ ] Analytics and reporting
- [ ] Webhook support for automation
- [ ] WebSocket for real-time updates

### v2.0.0
- [ ] Advanced NLP models
- [ ] Resume improvement suggestions
- [ ] ATS optimization scoring
- [ ] Job matching engine
- [ ] Mobile app
- [ ] API rate limiting and quotas

---

## Migration Guides

### From v0.1.0 to v1.0.0
1. Update Docker image: `docker pull resume-classifier:latest`
2. Set `HUGGINGFACE_API_KEY` environment variable
3. Run migrations: `python -m alembic upgrade head` (if needed)
4. Restart services: `docker compose restart`

---

## Support

For questions or issues:
- 🐛 [Report a bug](https://github.com/frankTheCodeBoy/ai_doc_classifier/issues)
- 💬 [Start a discussion](https://github.com/frankTheCodeBoy/ai_doc_classifier/discussions)
- 📖 [Read the docs](docs/)

---

**Last Updated**: 2026-05-29  
**Maintainer**: Francis Olum [@frankTheCodeBoy](https://github.com/frankTheCodeBoy)
