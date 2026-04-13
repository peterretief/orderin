# Screenshots & Images

Add application screenshots here to include in README and documentation.

## Recommended Screenshots

Place these screenshots in this directory:

1. **login.png** - Login page screenshot
   - Shows: Login form, error messages
   - Used in: README, authentication docs

2. **dashboard.png** - Main dashboard/home page
   - Shows: User dashboard, menu, key features
   - Used in: README, getting started guide

3. **profile-edit.png** - Profile editing interface
   - Shows: Profile form, all editable fields
   - Used in: User guides, feature documentation

4. **marketplace.png** - Product marketplace
   - Shows: Product listing, search, filters
   - Used in: Feature documentation

5. **order-checkout.png** - Order checkout page
   - Shows: Cart, address validation, checkout
   - Used in: User guides

6. **admin-panel.png** - Admin dashboard
   - Shows: Admin controls, user management
   - Used in: Administrator guide

## How to Add Screenshots

### On macOS
```bash
# Take screenshot
Cmd + Shift + 4

# Select area and save to Desktop
# Move to this directory
mv ~/Desktop/Screenshot*.png .
```

### On Windows
```bash
# Use Snip & Sketch (Win + Shift + S)
# Save to this directory
```

### On Linux
```bash
# Using GNOME Screenshot
gnome-screenshot -a

# Or use other tools like Flameshot
flameshot gui
```

## Image Guidelines

- **Format**: PNG or JPEG (PNG preferred)
- **Size**: 800x600 or 1024x768 pixels
- **Quality**: High quality, clear and readable
- **Content**: Relevant to the feature/guide
- **Privacy**: Remove any sensitive information
- **Naming**: Use descriptive names (e.g., `profile-edit.png`)

## Using in Documentation

To reference images in markdown:

```markdown
![Login Page](docs/images/login.png)

Or with alt text:
![Screenshot showing the login form with username and password fields](docs/images/login.png)
```

## Current Images

Currently no screenshots have been added. Please contribute screenshots to improve documentation!

To add screenshots:
1. Take screenshots as described above
2. Save them to this directory (`docs/images/`)
3. Update README files to reference them
4. Commit and push to GitHub
