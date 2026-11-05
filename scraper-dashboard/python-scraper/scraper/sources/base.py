class JobSourceAdapter:
    def discover(self):
        raise NotImplementedError("Subclasses must implement the discover method.")
    
    def fetch(self, url):
        raise NotImplementedError("Subclasses must implement the fetch method.")
    
    def parse(self, payload):
        raise NotImplementedError("Subclasses must implement the parse method.")
    
    def canonicalize_url(self, url):
        raise NotImplementedError("Subclasses must implement the canonicalize_url method.")
    
    def source_external_id(self, raw_job):
        raise NotImplementedError("Subclasses must implement the source_external_id method.")
    
adapter = JobSourceAdapter()
    
    
