# Pull Request Template

Thank you for contributing to FiveTwenty! Please fill out this template to help us review your changes effectively.

---

## Description

### **What does this PR do?**

Brief description of the changes and their purpose.

### **What problem does it solve?**

- Link to GitHub issue (if applicable): Fixes #123
- Description of the problem or feature request

### **How does it solve the problem?**

- Approach taken
- Key implementation details
- Any architectural decisions made

---

## Type of Change

Please check the type of change your PR introduces:

- [ ] 🐛 **Bug fix** (non-breaking change that fixes an issue)
- [ ] ✨ **New feature** (non-breaking change that adds functionality)
- [ ] 💥 **Breaking change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 **Documentation** (updates to documentation only)
- [ ] 🧹 **Refactoring** (code changes that neither fix a bug nor add a feature)
- [ ] ⚡ **Performance** (changes that improve performance)
- [ ] 🧪 **Tests** (adding missing tests or correcting existing tests)
- [ ] 🔧 **Chore** (changes to build process, dependencies, etc.)

---

## Testing

### **Test Coverage**

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] Manual testing performed
- [ ] All existing tests pass

### **Test Results**

```bash
# Paste test output here
uv run poe test

# Example:
# ✅ 158 tests passed
# ✅ Coverage: 95%
# ✅ MyPy: No errors
# ✅ Ruff: No issues
```

### **Integration Testing**

If this PR affects API interactions:

- [ ] Tested with OANDA practice account
- [ ] VCR cassettes updated (if needed)
- [ ] Streaming functionality tested (if applicable)
- [ ] Error handling tested

---

## Code Quality

### **Automated Checks**

- [ ] `uv run poe check` passes without errors
- [ ] Code follows project style guidelines
- [ ] Type hints are complete and accurate
- [ ] All public APIs are documented

### **Security Considerations**

- [ ] No credentials or sensitive data exposed
- [ ] Decimal types used for financial calculations
- [ ] Input validation appropriate for user-facing methods
- [ ] Error messages don't leak sensitive information

### **Performance Impact**

- [ ] No negative performance impact identified
- [ ] Memory usage is reasonable
- [ ] Streaming performance maintained (if applicable)
- [ ] Concurrent operation support maintained

---

## Documentation

### **Documentation Updates**

- [ ] API reference updated (if adding/changing public methods)
- [ ] Examples updated (if changing existing behavior)
- [ ] Tutorials updated (if relevant)
- [ ] CHANGELOG.md updated

### **Breaking Changes**

If this is a breaking change, please describe:

1. **What breaks**: Specific APIs or behaviors that change
2. **Migration path**: How users should update their code
3. **Justification**: Why the breaking change is necessary

---

## Compatibility

### **Python Versions**

- [ ] Tested with Python 3.10+
- [ ] Uses only features available in minimum Python version
- [ ] Type hints compatible with supported versions

### **Dependencies**

- [ ] No new runtime dependencies added (or justified)
- [ ] Development dependencies are appropriate
- [ ] Version constraints are reasonable

### **OANDA API Compatibility**

- [ ] Compatible with OANDA v20 REST API
- [ ] Follows OANDA API conventions
- [ ] Error codes match OANDA specifications
- [ ] Field names use proper aliases for API compatibility

---

## Review Checklist

### **Code Review Focus Areas**

Please review the following areas carefully:

1. **Correctness**: Does the code work as intended?
2. **Security**: Are credentials handled safely?
3. **Performance**: Any negative impacts?
4. **Testing**: Adequate test coverage?
5. **Documentation**: Public APIs documented?
6. **Consistency**: Follows existing patterns?

### **Specific Review Requests**

If you'd like reviewers to focus on specific areas:

- [ ] Architecture/design decisions
- [ ] Performance implications
- [ ] Security considerations
- [ ] API design
- [ ] Error handling
- [ ] Test strategy

---

## Deployment Considerations

### **Rollout Plan**

For significant changes:

- [ ] Gradual rollout strategy considered
- [ ] Backward compatibility maintained
- [ ] Feature flags used (if applicable)
- [ ] Monitoring plan in place

### **Risk Assessment**

- **Low Risk**: Documentation, tests, internal refactoring
- **Medium Risk**: New features, performance improvements
- **High Risk**: Breaking changes, core architecture changes

**Risk Level**: [ Low / Medium / High ]

**Risk Mitigation**: (Describe steps taken to minimize risk)

---

## Additional Context

### **Related Work**

- Related PRs: #123, #456
- Related issues: #789
- External references: Links to OANDA documentation, etc.

### **Future Work**

- Follow-up tasks needed
- Technical debt introduced (if any)
- Potential improvements identified

### **Questions for Reviewers**

- Specific questions about the implementation
- Trade-offs you're unsure about
- Areas where you'd like feedback

---

## Reviewer Assignment

**Suggested Reviewers**: @username1, @username2

**Why**: Expertise in affected areas, context on related work

---

**Thank you for contributing to FiveTwenty! 🚀**

Please ensure all checkboxes are completed before requesting review. This helps maintainers provide faster, more focused feedback.