cv-parser
=========

An api to parse a CV, in particular the elements of its publication list.

To deploy, use custom buildpack:

heroku config:set BUILDPACK_URL=https://github.com/stochastic-technologies/impactstory-buildpack.git -a heroku_app_name

Accepts POST requests to /parsecv/ either with a "url" field or a "file" field for pdf files.

URLs can point to a Mendeley user profile or a custom HTML CV.
The only accepted file format is PDF. Multicolumn PDFs produce unpredictable results.
Non-standard citation formats are parsed with less accuracy due to the training dataset
using mostly standard citations. 

Rate limiting is currently turned off due to the lack of a redis server
on the test heroku instance. 

To activate, uncomment the lines before and after the parse_request() method.
