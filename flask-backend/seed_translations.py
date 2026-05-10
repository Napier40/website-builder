"""
Seed English translations (principal language).
English is the fallback language and all keys must exist.

Run: python seed_translations.py
"""
from app import create_app
from app.database import db
from app.models.translation import Translation


# English translations
ENGLISH_TRANSLATIONS = {
    # Common translations
    'common': {
        'appName': 'Website Builder',
        'appNameShort': 'Builder',
        'save': 'Save',
        'cancel': 'Cancel',
        'delete': 'Delete',
        'edit': 'Edit',
        'create': 'Create',
        'update': 'Update',
        'name': 'Name',
        'description': 'Description',
        'close': 'Close',
        'confirm': 'Confirm',
        'loading': 'Loading...',
        'search': 'Search',
        'filter': 'Filter',
        'sort': 'Sort',
        'all': 'All',
        'none': 'None',
        'yes': 'Yes',
        'no': 'No',
        'or': 'or',
        'and': 'and',
        'optional': 'optional',
        'required': 'required',
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Information',
        'home': 'Home',
        'dashboard': 'Dashboard',
        'settings': 'Settings',
        'profile': 'Profile',
        'logout': 'Logout',
        'login': 'Login',
        'signup': 'Sign Up',
        'email': 'Email',
        'password': 'Password',
        'username': 'Username',
        'back': 'Back',
        'next': 'Next',
        'previous': 'Previous',
        'continue': 'Continue',
        'submit': 'Submit',
        'reset': 'Reset',
        'clear': 'Clear',
        'upload': 'Upload',
        'download': 'Download',
        'copy': 'Copy',
        'paste': 'Paste',
        'cut': 'Cut',
        'undo': 'Undo',
        'redo': 'Redo',
    },

    # Builder-specific translations
    'builder': {
        'pageTitle': 'Website Builder',
        'selectComponent': 'Select a component to edit its properties',
        'dragToCanvas': 'Drag components to the canvas',
        'dropHere': 'Drop here',
        'addChild': 'Add child element',
        'duplicate': 'Duplicate',
        'remove': 'Remove',
        'moveUp': 'Move up',
        'moveDown': 'Move down',
        'properties': 'Properties',
        'canvas': 'Canvas',
        'elements': 'Elements',
        'pages': 'Pages',
        'theme': 'Theme',
        'preview': 'Preview',
        'saveSuccess': 'Saved successfully',
        'saveError': 'Failed to save',
        'unsavedChanges': 'You have unsaved changes',
        'leavePage': 'Are you sure you want to leave? Your changes will be lost.',
        'autoSaving': 'Auto-saving...',
        'autoSaved': 'Auto-saved',
        'addPage': 'Add Page',
        'renamePage': 'Rename Page',
        'deletePage': 'Delete Page',
        'deletePageConfirm': 'Are you sure you want to delete this page?',
        'pageName': 'Page Name',
        'pageSlug': 'URL Slug',
        'device': 'Device',
        'mobile': 'Mobile',
        'tablet': 'Tablet',
        'desktop': 'Desktop',
        'publish': 'Publish',
        'unpublish': 'Unpublish',
        'published': 'Published',
        'draft': 'Draft',
        'websiteName': 'Website Name',
        'subdomain': 'Subdomain',
        'publishedUrl': 'Published URL',
        'noWebsite': 'No website selected',
        'createWebsite': 'Create Website',
        'startBlank': 'Start Blank',
        'startFromTemplate': 'Start from Template',
        'templateGallery': 'Template Gallery',
        'useTemplate': 'Use this Template',
        'templatePreview': 'Template Preview',
    },

    # Template translations
    'templates': {
        'title': 'Templates',
        'galleryTitle': 'Template Gallery',
        'allTemplates': 'All Templates',
        'freeTemplates': 'Free Templates',
        'premiumTemplates': 'Premium Templates',
        'filterByCategory': 'Filter by Category',
        'searchTemplates': 'Search templates...',
        'templateCount': '{count} templates',
        'cloneTemplate': 'Clone Template',
        'cloneSuccess': 'Website created from template!',
        'cloneError': 'Failed to create website from template.',
        'categoryLanding': 'Landing Pages',
        'categoryPortfolio': 'Portfolios',
        'categoryBlog': 'Blogs',
        'categoryBusiness': 'Business',
        'categoryEcommerce': 'E-commerce',
        'categoryRestaurant': 'Restaurants',
        'categoryResume': 'Resumes',
        'categoryEvent': 'Events',
        'categoryNonprofit': 'Non-profit',
        'categoryComingSoon': 'Coming Soon',
    },

    # Validation messages
    'validation': {
        'required': 'This field is required',
        'invalidEmail': 'Please enter a valid email address',
        'invalidUrl': 'Please enter a valid URL',
        'passwordTooShort': 'Password must be at least 8 characters',
        'passwordMismatch': 'Passwords do not match',
        'subdomainTaken': 'This subdomain is already taken',
        'subdomainInvalid': 'Subdomain can only contain letters, numbers, and hyphens',
        'nameTooShort': 'Name must be at least 2 characters',
        'nameTooLong': 'Name must be less than 200 characters',
    },

    # Auth translations
    'auth': {
        'loginTitle': 'Login to Your Account',
        'signupTitle': 'Create an Account',
        'forgotPassword': 'Forgot Password?',
        'rememberMe': 'Remember me',
        'noAccount': "Don't have an account?",
        'hasAccount': 'Already have an account?',
        'loginSuccess': 'Logged in successfully',
        'loginError': 'Login failed. Please check your credentials.',
        'signupSuccess': 'Account created successfully',
        'signupError': 'Failed to create account. Please try again.',
        'logoutSuccess': 'Logged out successfully',
    },

    # Error messages
    'errors': {
        'generic': 'An error occurred. Please try again.',
        'network': 'Network error. Please check your connection.',
        'unauthorized': 'You are not authorized to perform this action.',
        'notFound': 'The requested resource was not found.',
        'serverError': 'Server error. Please try again later.',
        'timeout': 'Request timed out. Please try again.',
    },
}


def seed_translations():
    """Seed English translations into the database."""
    app = create_app('development')
    with app.app_context():
        count = Translation.bulk_upsert(ENGLISH_TRANSLATIONS, language='en')

        print(f"{'='*60}")
        print(f"Seeding English translations complete!")
        print(f"  Total translations: {count}")
        print(f"{'='*60}")

        # Show summary by namespace
        namespaces = {}
        for row in Translation.query.filter_by(language='en').all():
            ns = row.namespace or 'common'
            if ns not in namespaces:
                namespaces[ns] = 0
            namespaces[ns] += 1

        print(f"\nTranslations per namespace:")
        for ns in sorted(namespaces.keys()):
            print(f"  {ns}: {namespaces[ns]} translations")


if __name__ == '__main__':
    seed_translations()