class CacheControlMiddleware(object):
  def process_response(self, request, response):
    if response['Content-Type'].startswith("text/html"):
      response['Cache-Control'] = \
          'no-store, no-cache, must-revalidate, private'
      response['Pragma'] = 'no-cache'
      return response
    return response
