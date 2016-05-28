# Flask-Locales

A Flask Extension that leverages Jinja's built-in template inheritance and context functionality to implement simple and organized document localization.

Provides several options for how localized content is implemented, providing flexibility in how each page is organized, and also allowing that organization to evolve with a project. Localized content can be implemented as simple alternate templates, be located within child templates, or loaded from files on the filesystem.

This is a pretty simple extension that, in most cases, abstracts all consideration of locales out of your view functions, yet automatically selects and renders the correct template and/or content according to the current locale.

For more information, take a look at the [Locales wiki](https://github.com/garyhurtz/Flask-Locales/wiki)
