# 🚀 Documentation Deployment Guide

This guide covers deploying the FiveTwenty documentation to production using GitHub Pages.

## 📋 Pre-Deployment Checklist

Before deploying, ensure all requirements are met:

### 1. Run Deployment Readiness Check

```bash
# Run comprehensive documentation validation
cd docs-tooling/validation
uv run python cli.py run --parallel --gates --report

# Check individual validators
uv run python cli.py run links
uv run python cli.py run prose
uv run python cli.py run syntax
uv run python cli.py run terminology
uv run python cli.py run security
```

### 2. Manual Verification Steps

- [ ] All documentation sections are complete
- [ ] Code examples are tested and working
- [ ] Internal links are valid
- [ ] API reference is up to date
- [ ] GitHub Actions workflows are configured
- [ ] Repository has GitHub Pages enabled

## 🔧 GitHub Repository Configuration

### Enable GitHub Pages

1. Go to repository **Settings** → **Pages**
2. Set **Source** to "Deploy from a branch"
3. Select **Branch**: `gh-pages`
4. Set **Folder**: `/ (root)`
5. Click **Save**

### Configure Repository Settings

Ensure your repository has these settings:

- **Visibility**: Public (required for free GitHub Pages)
- **Actions**: Enabled with read/write permissions
- **Pages**: Configured as described above

### Environment Variables (Optional)

For advanced deployments, you can set these repository secrets:

```bash
# Not required for basic GitHub Pages deployment
# CUSTOM_DOMAIN=docs.yourdomain.com  # For custom domain
# ANALYTICS_ID=G-XXXXXXXXXX         # For Google Analytics
```

## 🚀 Deployment Process

### Automatic Deployment (Recommended)

Documentation automatically deploys when changes are pushed to `main`:

```bash
# Make your documentation changes
git add docs/
git commit -m "Update documentation"
git push origin main

# GitHub Actions will:
# 1. Validate documentation
# 2. Build the site
# 3. Deploy to GitHub Pages
```

### Manual Deployment

For manual deployment or testing:

```bash
# 1. Validate documentation
cd docs-tooling/validation && uv run python cli.py run --parallel --gates

# 2. Build the site locally
uv run mkdocs serve  # Test locally at http://localhost:8000

# 3. Deploy to GitHub Pages
uv run mkdocs gh-deploy --clean --message "Manual deployment $(date)"
```

## 📊 Monitoring and Maintenance

### GitHub Actions Monitoring

Monitor deployments in the **Actions** tab:

- **Documentation** workflow: Validates and deploys on push
- **Documentation Maintenance** workflow: Weekly health checks

### Access Your Deployed Documentation

After deployment, your documentation will be available at:

```
https://nimbleox.github.io/fivetwenty/
```

### Weekly Maintenance

The automated maintenance workflow runs every Sunday and:

- Validates all documentation
- Checks for broken links
- Reviews dependency freshness
- Creates issues for any problems found

## 🔄 Update Process

### Regular Updates

1. **Content Updates**: Edit markdown files in `docs/`
2. **API Changes**: Update API reference documentation
3. **Examples**: Keep code examples current with SDK changes
4. **Dependencies**: Update `docs/requirements.txt` as needed

### Version-Specific Documentation

For versioned documentation:

```bash
# Create version-specific branch
git checkout -b docs/v2.0

# Update version-specific content
# Deploy version-specific docs
uv run mkdocs gh-deploy --clean --message "Deploy v2.0 docs"
```

## 🛠️ Troubleshooting

### Common Deployment Issues

**Build Failures:**
```bash
# Check validation
cd docs-tooling/validation && uv run python cli.py run --parallel

# Check MkDocs configuration
uv run mkdocs build --strict
```

**GitHub Actions Failures:**
```bash
# Check workflow logs in GitHub Actions tab
# Common issues:
# - Permission errors: Check repository settings
# - Build errors: Run validation locally first
# - Deployment errors: Verify GitHub Pages configuration
```

**Missing Content:**
```bash
# Verify all sections exist
ls docs/
# Should include: getting-started, user-guide, api-reference, tutorials, examples
```

### Performance Optimization

**Large Site Optimization:**
```yaml
# In mkdocs.yml, add:
plugins:
  - search:
      prebuild_index: true
  - minify:
      minify_html: true
```

**Image Optimization:**
```bash
# Optimize images before adding to docs
# Use tools like imagemin or manual compression
```

## 🎯 Best Practices

### Content Management

1. **Consistency**: Follow established style guide
2. **Accuracy**: Keep code examples tested and current
3. **Navigation**: Maintain clear information architecture
4. **Performance**: Optimize images and minimize large files

### Deployment Workflow

1. **Always validate** before deploying
2. **Use staging** for major changes
3. **Monitor metrics** after deployment
4. **Keep backups** of previous versions

### Security Considerations

1. **No secrets**: Never commit API keys or tokens
2. **Clean examples**: Use placeholder values in code
3. **Access control**: Monitor repository permissions
4. **HTTPS**: Ensure secure delivery (GitHub Pages default)

## 📈 Success Metrics

Track these metrics post-deployment:

### User Experience
- Page load times < 2 seconds
- Mobile responsiveness score > 90%
- Search functionality working
- All links functional

### Content Quality
- Zero broken internal links
- All code examples syntactically valid
- Complete API coverage
- Up-to-date screenshots and examples

### Technical Health
- Successful automated builds
- No deployment failures
- Clean validation reports
- Regular maintenance completion

## 🆘 Emergency Procedures

### Rollback Process

If issues are found post-deployment:

```bash
# Option 1: Quick rollback to previous commit
git revert HEAD
git push origin main

# Option 2: Deploy previous known-good state
git checkout <previous-good-commit>
uv run mkdocs gh-deploy --clean --message "Emergency rollback"
```

### Hotfix Process

For critical documentation fixes:

```bash
# Create hotfix branch
git checkout -b hotfix/critical-fix

# Make minimal necessary changes
# Test thoroughly
cd docs-tooling/validation && uv run python cli.py run --gates

# Deploy immediately
git push origin main
```

---

## 📞 Support and Resources

- **Documentation Issues**: Use repository issue tracker
- **GitHub Pages Help**: [GitHub Pages Documentation](https://docs.github.com/en/pages)
- **MkDocs Help**: [MkDocs Documentation](https://www.mkdocs.org/)
- **Maintenance**: Automated weekly reports provide ongoing health monitoring

**Ready to deploy?** Run the readiness checker and follow the deployment process above! 🚀