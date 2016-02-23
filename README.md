# Layer-Rails

> Juju charms.reactive layer for a Rails application

## emitters

**website.configured** - This state is set when the application has been setup and is running.

## Configuration

repo: The git repository to clone from **Required**
deploy_key: A deploy key is an SSH key that is stored on the server and grants access to a repository.
app-path: Where on the filesystem to run the app
web_workers: How many Puma processes to use
worker_threads: How many threads to use per worker
web_port: Port to listen on
domain: Domain name to use

## Relations

### PostgreSQL

This allows the user to attach PostgreSQL for Rails to make use of.

### HTTP



# license

The MIT License (MIT)

Copyright (c) 2015 Chris MacNaughton <chris.macnaughton@canonical.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.