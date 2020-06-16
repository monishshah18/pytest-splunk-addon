import re
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")

class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """

    def __init__(self, event_string, metadata):
        self.event = event_string
        # self.host = str
        # self.sourcetype = str
        # self.source = str
        # self.ingest_type = str
        self.key_fields = dict()
        self.metadata = metadata

    def update(self, new_event):
        self.event = new_event

    def get_token_count(self, token):
        return len(re.findall(token, self.event))

    def replace_token(self, token, token_values):
        # TODO: How to handle dependent Values with list of token_values
        if isinstance(token_values, list):
            for token_value in token_values:
                self.event = re.sub(
                    token, str(token_value), self.event, 1, flags=re.MULTILINE
                )
        else:
            self.event = re.sub(
                token, str(token_values), self.event, flags=re.MULTILINE
            )

    def register_field_value(self, field, token_values):
        if isinstance(token_values, list):
            for token_value in token_values:
                self.key_fields.setdefault(field, []).append(token_value)
        else:
            self.key_fields.setdefault(field, []).append(token_values)

    def get_key_fields(self):
        return self.key_fields

    @classmethod
    def copy(cls, event):
        new_event = cls("", {})
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        return new_event

    def update_metadata(self, event, metadata):
        """
        This method is to process the syslog formated samples data
        data: raw syslog data
            data_format::
                ***SPLUNK*** source=<source> sourcetype=<sourcetype>

                fiels_1       field2        field3
                ##value1##    ##value2##   ##value3##
            metadata: dictionary of metadata
            params_format::
                {
                    "host": "sample_host",
                    "source": "sample_source"
                }
        Returns:
            syslog data and params that contains syslog_headers
        """
        try:
            if isinstance(event, str) and event.startswith("***SPLUNK***"):
                header = event.split("\n", 1)[0]
                self.event = event.split("\n", 1)[1]

                meta_fields = re.findall(r"[\w]+=[^\s]+", header)
                for meta_field in meta_fields:
                    field = meta_field.split("=")[0]
                    value = meta_field.split("=")[1]
                    self.metadata[field] = value

                return self.event, self.metadata
            else:
                return event, metadata
        except IndexError as error:
            LOGGER.error(f"Unexpected data found. Error: {error}")
            raise Exception(error)
