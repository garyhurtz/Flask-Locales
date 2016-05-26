# Flask-Locales

A Flask Extension that leverages Jinja's built-in template inheritance and context functionality to implement simple and organized document localization.

Provides several options for how localized content is implemented, providing flexibility in how each page is organized, and also allowing that organization to evolve with a project. Localized content can be implemented as simple alternate templates, be located within child templates, or loaded from files on the filesystem.

This is a pretty simple extension that, in most cases, abstracts all consideration of locales out of your view functions, yet automatically selects and renders the correct template and/or content according to the current locale.

# Setup

Flask extensions can be set up several ways, but in general looks something like this:

    from flask import Flask
    from Locales import Locales
    
    class CONFIG(object):
    
        # required to enable sessions in Flask
        # obviously, change to something more secret
        SECRET_KEY = u'0123456789'
        
        # the locales that are supported in this application
        # formatted as (name, tag) pairs
        # name is the internal reference to each locale
        # tag is the representation of this locale in views
        LOCALES = [
            (u'en', u'EN'),
            (u'zh_Hans', u'中文')
        ]
        
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(CONFIG)
    
    Locales(app)

After applying the extension, the API is available in view functions at *g.locales*.

# API

## Properties

### *current*

Get the name of the current locale.

At the start of each request, Locales checks the *session* to see if a locale has been set. If not (such as on the first request of a new session) the extension attempts to find the best match based on browser settings. If a best match cannot be identified, the default locale (as specified in the application config) is used. This behavior ensures that *current* always stores a valid locale.
        
### *next*

Return the name of the next locale, as defined in application config. This is useful in applications that use *toggle()* to iterate through available locales.

### *default*

Return the name of the default locale

## Methods

### *toggle()*

Transition to the next locale, in the order defined in the application configuration. Convenient if you use a simple toggle button to iterate through available locales.

### *render_template(template_name_or_list, static_context=None, \**context)*

A wrapper around Flask's *render_template* function, which imports localized content when it is available, and falls back to the default Flask *render_template* function when it isn't.

#### **template_name_or_list**:
 
Per Flask default, templates are organized within *template_folder*, as defined in the app configuration. Localized templates are organized within sub-folders of *template_folder*, with each sub-folder corresponding to a unique locale.
 
Given a template name, the extension first attempts to retrieve the template from within a localized template folder, then if the template is not found falls back to the default Flask behavior. In other words, extension attempts to retrieve the template from the following locations, and in the following order:

<table>
<tr>
<th>If Blueprints are not used</th>
<th>If Blueprints are used</th>
</tr>
<tr>
<td>template_folder/current_locale/template_name</td> 
<td>template_folder/blueprint/current_locale/template_name</td>
</tr>
<tr>
<td>template_folder/template_name</td> 
<td>template_folder/blueprint_name/template_name</td>
</tr>
</table>
    
Note that *template_folder* is specified for completeness, but template paths are specified relative to the *template_folder*. The search terminates as soon as the first template is found.

Like Flask's *render_template*, the extension also accepts a list of template names. When a list of template names is passed, the extension will search for each *localized* template first, then fall back to each given template name if none is found.

Note the following:

1) This extension does not currently support Blueprint-specific template folders, although it may in the future.

2) In order to resolve template paths correctly, templates must reside at the root level of each locale sub-folder.
 
#### **static_context**

Generally speaking, Jinja templates contain pseudo-static information and, optionally, some *variables* that get populated with values from the context dictionary when the template is rendered.

In addition to supporting localized content within the templates themselves, this extension also supports passing localized content to the template when it is rendered. This content is loaded from files on the local filesystem and passed to templates when they render, and is referred to as the *static_context* in order to differentiate it from the (dynamic) context.

To be more specific, the **static_context** keyword argument is an optional string parameter that specifies the path from which you wish to load localized content. This path is specified relative to the *context* folder, which exists at the root level of the project directory. Just like templates, the extension modifies this path in order to load localized content, if it is available, as shown on the following table:

<table>
<tr>
<th>If Blueprints are not used</th>
<th>If Blueprints are used</th>
</tr>
<tr>
<td>context_folder/current_locale/context_path</td> 
<td>context_folder/blueprint/current_locale/context_path</td>
</tr>
<tr>
<td>context_folder/context_path</td> 
<td>context_folder/blueprint_name/context_path</td>
</tr>
<tr>
<td>context_path</td> 
<td>context_folder/context_path</td>
</tr>
</table>

This table specifies the *context_folder* to be explicit, but paths are specified relative to this folder.

##### *common context*

The preceding table indicates that the context search path is the same as that used for templates, but consists of one additional step; the extension allows the *static_context* to be specified as a single file located at the root level of the application or blueprint. In some cases defining all localized content within a single file, rather than organizing it within a localized directory structure, can have advantages so the extension makes this option available. This case is referred to as a *common context*, since all localized content is contained within a common file.

So how does this work? First, the file should be organized like this:

    key: value pairs that are available to all locales
   
    <locale 1>:
   
      key: value pairs that are available when <locale 1> renders
     
    <locale 2>:
   
      key: value pairs that are available when <locale 2> renders

Next, when a common context is loaded, the extension loads the file, then promotes any key: value pairs under the current locale to the root level before the context is passed to the template. That's about it, although there are a few things to point out:

* Keys from the current locale take precedence over common keys, meaning that common keys will be replaced by localized keys, if present.

* Although variables from the current locale are promoted to the top level, all locale information remains available. It is therefore possible to render a value from a specific locale doing something like {{ zh_Hans.greeting }}.

* Common context requires loading all localized content for all locales, every time the template is rendered. This can have an impact on speed and efficiency, so common context is generally most appropriate:

  1) in the early stages of developing a page (during mock-ups, etc) when developer time is more important than rendering speed, 
  
  2) when there is only a small amount of localized content, so organizing into separate files doesn't make sense, or 
  
  3) for low-traffic pages where there may not be much benefit to optimizing.

We will take a look at a few examples below that should help clarify everything.

**context**

Of course, there is also dynamic information that can change from request to request, which is referred to as the *context* in order to remain consistent with Flask naming conventions. The extension treats the *context* identically to Flask.

### *load(path)*

Load context information from path.

## Template Globals

### current_locale()

Return the name of the current locale.

### next_locale_tag()

Return the tag for the next locale. This is useful for functions that use the *toggle* functionality.

## Template Filters

### tag(locale)

Return the tag corresponding to *locale*, as defined in the LOCALES property of the application config.

# Context Loaders

Context loaders are functions that:

1) take a path string, and

2) return the context as a Python dictionary

Locales ships with few context loaders, and custom context loaders can be added as needed to support other file formats. Current built-in context loaders include:

* **yaml_loader** - the default loader, loads content from yaml files (assumes \*.yaml suffix). YAML provides a relatively user-friendly format for defining localized content, but parses relatively slowly so this loader may not be suitable for high-traffic sites. You can learn more about YAML [here](http://yaml.org/).

* **json_loader** - an alternative loader, which has a less user-friendly file format, but parses significantly faster (~50x faster, in my tests). This loader is very useful if your workflow uses external code to generate the localized content files. You can generate them in any way you like, then export them as JSON into the appropriate directories. You can learn more about JSON [here](http://www.json.org/).

* **json_caching_yaml_loader** - an alternate loader for people who like YAML, but want better performance. Benefits from YAML as a user interface, but caches the content in JSON format to benefit from it's improved parsing speed. This is the recommended loader, but is not used by default since it generates cache folders.

Context loaders are pretty simple, for example here is the JSON loader:

    def load_json(cls, path):

        with codecs.open(os.path.join(current_app, path)) as infile:
            context = json.load(infile)

        return context

And you can apply it when you set up your app like this:

    Locales(app)
    Locales.context_loader = load_json

Context loaders are applied as class methods, which explains why you need the *cls* reference as the first argument. This also provides access to the class, if you need it within the loader.

Next, you pass the loader the path to the file to load. Path localization, etc is handled for you before the loader is called, so all you need to do is load the requested file and return the content.

# Examples

## Baseline Examples

### Flask *render_template*:

This example is the default Flask render_template, and is included to set a baseline comparison purposes.

Folder structure:

    application/
        routes.py
        templates/
            greeting.html

*greeting.html*:

    <p>Hello World!</p>

in the view function:

    from flask import render_template

    def view_function():
        return render_template('greeting.html')

the result:

    Hello World!

### Flask *render_template* With Blueprints:

Like the preceding example, this example shows the default Flask render_template with Blueprints, and is included as a baseline for comparison purposes.

Folder structure:

    application/
        blueprint/
            routes.py
        templates/
            blueprint/
                greeting.html
            
*blueprint/greeting.html*:

    <p>Hello World!</p>

in the view function:

    from flask import render_template

    def view_function():
        return render_template('blueprint/greeting.html')

the result:

    Hello World!

## Locales Examples

### Basic Setup

This is the basic setup, which is backwards-compatible with default Flask. Note that behavior is identical to that of the Flask example above.

The idea is that upgrading an existing site should require little more than searching & replacing *render_template* with *g.locales.render_template*. Of course, some adjustment may be required if your original directory structure is not compatible.

Folder structure:

    application/
        routes.py
        templates/
            greeting.html
            
*greeting.html*:

    <p>Hello World!</p>

in the view function:

    def view_function():
        return g.locales.render_template('greeting.html')

the result:

    Hello World!
    
### Basic Setup With Blueprints:

As with the preceding example, this extension is also backwards-compatible when using Blueprints, too.

Folder structure:

    application/
        blueprint/
            routes.py
        templates/
            blueprint/
                greeting.html
            
*blueprint/greeting.html*:

    <p>Hello World!</p>

in the view function:
    
    def view_function():
        return g.locales.render_template('blueprint/greeting.html')

the result:

    Hello World!

## Localized Template Examples:

### Basic

Here is the first example that actually uses some capability from the extension. Although you generally won't prepare completely separate documents for each locale, this example demonstrates how one would do so. This also provides a simplified example to give you a feel for how the extension works with the directory structure.

Folder structure:

    application/
        routes.py
        templates/
            en/
                greeting.html
            zh_Hans/
                greeting.html
                
*en/greeting.html*:

    <p>Hello World!</p>

*zh_Hans/greeting.html*:

    <p>你好世界!</p>
    
then the view function can be as simple as:

    def view_function():
        return g.locales.render_template('greeting.html')

the result (g.locales.current == 'en'):

    Hello World!

the result (g.locales.current == 'zh_Hans'):

    你好世界!

Note that no information about the current locale needs to be coded into the view function, and *render_template* is pointed to a path that doesn't even exist, yet the extension is able to select and render localized content.

### Basic with Blueprints:

It works pretty much the same with Blueprints too.

Folder structure:

    application/
        blueprint/
            routes.py
        templates/
            blueprint/
                en/
                    greeting.html
                zh_Hans/
                    greeting.html
                
*blueprint/en/greeting.html*:

    <p>Hello World!</p>

*blueprint/zh_Hans/greeting.html*:

    <p>你好世界!</p>
    
the view function remains very simple, and the extension still knows how select the localized template from within the blueprint template folder.

    def view_function():
        return g.locales.render_template('blueprint/greeting.html')

the result (g.locales.current == 'en'):

    Hello World!

the result (g.locales.current == 'zh_Hans'):

    你好世界!

## Template Inheritance

We have seen how the extension locates templates within the folder structure, so with the basic under our belt let's look at a slightly more realistic example.

This example uses a pattern that leverages Jinja's inheritance capabilities to pass localed content into a template.

Here is the folder structure:

    application/
        routes.py
        templates/
            greeting.html
            en/
                greeting.html
            zh_Hans/
                greeting.html
                
*greeting.html*, which includes some basic [Bootstrap](http://getbootstrap.com/) markup in addition to the variables:

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>{{ greeting }}</p>
            </div>
            
            <div class="paragraph">
                <p>{{ paragraph }}</p>
            </div>
        </div>
    </div> 
   
Next, each *<locale>/greeting.html* looks something like this (obviously, with localized content where applicable):

    {% extends 'greeting.html' %}
    
    {% set greeting = 'Hello World!' %}
    
    {% set paragraph %}
    Imagine a long paragraph of text here
    {% endset %}

In the view function:

    def view_function():
        return g.locales.render_template('greeting.html')

The result (assuming g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

Let's review: there is a master template *greeting.html* at the root level of the *template_folder*, and templates of the same name within each locale folder. *render_template* was told to render a file *greeting.html*, so the extension looked first for a localized template and found one located at *<current_locale>/greeting.html*. This template extends a master template *greeting.html*, however, so Jinja imported the master template, injected the localized content into it, and returned the result.

It is not necessary to give the master and child templates the same name, and deviating from this conventional may be necessary at times. The main requirements are:

1) child templates be given the same names, so that the path localization process can select them correctly, 

2) *render_template* must be passed the name of the **child** template, which will be localized, and

3) the child templates must *extend* a common master template.

IMHO, however, maintaining direct associations between child and master templates, as shown in the example, helps keep everything organized as the project grows.

Note that once the localized templates were found, this pattern leveraged Jinja template inheritance to do the heavy lifting, and therefore this pattern benefits from Jinja caching. This makes this pattern a good choice if the markup in the child templates isn't too much of a burden, such as when a page consists mainly of paragraphs of text.

## Template Inheritance with Blueprints

Here is a repeat of the preceding example, with Blueprints. The key points are that you have to specify the template paths relative to the blueprint sub-folder. Otherwise, all of the same comments apply.

Here is the folder structure:

    application/
        blueprint/
            routes.py
        templates/
            blueprint/
                greeting.html
                en/
                    greeting.html
                zh_Hans/
                    greeting.html
                
*blueprint/greeting.html*:

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>{{ greeting }}</p>
            </div>
            
            <div class="paragraph">
                <p>{{ paragraph }}</p>
            </div>
        </div>
    </div> 
   
Each *blueprint/<locale>/greeting.html* (again, with localized content where applicable):

    {% extends 'blueprint/greeting.html' %}
    
    {% set greeting = 'Hello World!' %}
    
    {% set paragraph %}
    Imagine a long paragraph of text here
    {% endset %}

In the view function:

    def view_function():
        return g.locales.render_template('blueprint/greeting.html')

The result (assuming g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

## Static Context Examples:

We have looked at a few examples of how templates are located within the directory structure, so lets now look at some example for how static contexts are handled.

### Basic

Our first example uses a single master template that is populated with localized content from the *static context*, and uses the following folder structure:

    application/
        routes.py
        context/
            en/
                context.yaml
            zh_Hans/
                context.yaml
        templates/
            greeting.html

Similar to the *templates* folder from previous examples, this example introduces a *context* folder that contains localized sub-directories.

*greeting.html*:

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>{{ greeting }}</p>
            </div>
            
            <div class="paragraph">
                <p>{{ paragraph }}</p>
            </div>
        </div>
    </div> 

context/en/context.yaml:

    greeting: Hello World!
    paragraph: Imagine a long paragraph of text here
    
context/zh_Hans/context.yaml:
    
    greeting: 你好世界!
    paragraph: 想象这里的文字长款
      
In the view function:

    def view_function():
        return g.locales.render_template('greeting.html', 'context.yaml')
        
the result (g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

the result (g.locales.current == 'zh_Hans'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>你好世界!</p>
            </div>
            
            <div class="paragraph">
                <p>想象这里的文字长款</p>
            </div>
        </div>
    </div>

So, as with previous examples, the extension was able to locate the correct localized content and render it with the template.

### Basic with Blueprints

This is how it would look with Blueprints:

    application/
        blueprint/
            routes.py
            context/
                en/
                    context.yaml
                zh_Hans/
                    context.yaml
        templates/
            blueprint/
                greeting.html

*blueprint/greeting.html*:

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>{{ greeting }}</p>
            </div>
            
            <div class="paragraph">
                <p>{{ paragraph }}</p>
            </div>
        </div>
    </div> 

blueprint/context/en/context.yaml:

    greeting: Hello World!
    paragraph: Imagine a long paragraph of text here
    
blueprint/context/zh_Hans/context.yaml:

    greeting: 你好世界!
    paragraph: 想象这里的文字长款
      
In the view function:

    def view_function():
        return g.locales.render_template('blueprint/greeting.html', 'blueprint/context.yaml')
        
the result (g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

the result (g.locales.current == 'zh_Hans'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>你好世界!</p>
            </div>
            
            <div class="paragraph">
                <p>想象这里的文字长款</p>
            </div>
        </div>
    </div>

## Common Context

### Basic

So, you basically work with the static context just as you would with templates. But, with one exception, the common context.

As discussed earlier, the common context is a single file that contains all localized content, organized under keys that correspond to each supported locale.

The folder structure:

    application/
        routes.py
        context.yaml
        templates/
            greeting.html
            
context.yaml:
    
    a: few
    common: variables

    en:
      greeting: Hello World!
      paragraph: Imagine a long paragraph of text here

    zh_Hans:
      greeting: 你好世界!
      paragraph: 想象这里的文字长款
   
In the view function:

    def view_function():
        return g.locales.render_template('greeting.html', 'context.yaml')
        
the result (g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

the result (g.locales.current == 'zh_Hans'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>你好世界!</p>
            </div>
            
            <div class="paragraph">
                <p>想象这里的文字长款</p>
            </div>
        </div>
    </div>
    
So, what happened here? First, the extension looked for localized content under the *context_folder*, but none exists so it eventually loads *context.yaml* directly from the root folder. When this happens, the extension recognizes that it is loading a common context, and treats it slightly differently. As mentioned above, if it finds a key that corresponds to the current locale, variables under that key are "promoted" to the root level so that the template can access them. In this example, the *common context* gets transformed into this:

    a: few
    common: variables
    greeting: Hello World!
    paragraph: Imagine a long paragraph of text here
      
    en:
      greeting: Hello World!
      paragraph: Imagine a long paragraph of text here

    zh_Hans:
      greeting: 你好世界!
      paragraph: 想象这里的文字长款

then gets passed to the template. The template contains *greeting* and *paragraph* variables, which can now be populated.

Note that no information was lost in the process, although common variables will get overwritten by localized variables with the same keys, if they exist. Templates are still able to directly reference variables from any locale, i.e. {{ zh_Hans.greeting }}.
    
### Basic with Blueprints

Here is how the previous example would look if the project were to use Blueprints:

Folder structure:

    application/
        blueprint/
            routes.py
            context.yaml
        templates/
            blueprint/
                greeting.html
            
context.yaml:

    a: few
    common: variables

    en:
      greeting: Hello World!
      paragraph: Imagine a long paragraph of text here

    zh_Hans:
      greeting: 你好世界!
      paragraph: 想象这里的文字长款

In the view function:

    def view_function():
        return g.locales.render_template('blueprint/greeting.html', 'blueprint/context.yaml')
        
the result (g.locales.current == 'en'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>Hello World!</p>
            </div>
            
            <div class="paragraph">
                <p>Imagine a long paragraph of text here</p>
            </div>
        </div>
    </div>

the result (g.locales.current == 'zh_Hans'):

    <div class="row">
        <div class="col-md-offset-3 col-md-6">
            <div class="greeting">
                <p>你好世界!</p>
            </div>
            
            <div class="paragraph">
                <p>想象这里的文字长款</p>
            </div>
        </div>
    </div>
    
# TODO List

1) deploy

  I developed this code as I developed one of my websites, but (long story...) I didn't write it as a stand-alone extension. The goal of this project is to refactor it into a stand-alone extension, which is complete, but I have not refactored the original project to use this extension yet. While I don't expect problems, I consider this to be a work in progress until that is complete.
  
2) template_caching_yaml_loader

  The *json_caching_yaml_loader* works pretty well, but I really want to export child templates directly since this would eliminate the need to parse the context prior to rendering, provide the speed benefits of Jinja caching, and also eliminate the cache folders that get injected into the project directories (with the *json_caching_yaml_loader*). Seems like it should be straight-forward, though.

3) Blueprint-specific template folders
 
  I personally prefer organizing templates into a single template folder, but recognize that others have their preferences too. This seems doable, although there are some quirks to how Flask handles Blueprint-specific template folders that may have to be worked out.
