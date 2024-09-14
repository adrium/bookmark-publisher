# Bookmark Publisher

Takes the Chrome `Bookmarks` file as input and generates
a list based on a template from a subset of it.

Uses [Handlebars](https://handlebarsjs.com/) templates.
Recommended to install [pybars4](https://github.com/up9inc/pybars4).
(One of the Mustache-like engines that supports recursive templates.)

	python bookmark-publisher.py guid.json playlist.json
	python bookmark-publisher.py guid.json html.json
