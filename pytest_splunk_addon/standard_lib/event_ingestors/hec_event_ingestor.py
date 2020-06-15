"""
HEC Event Ingestor class
"""
from base_event_ingestor import EventIngestor
import requests

requests.urllib3.disable_warnings()


class HECEventIngestor(EventIngestor):
    """
    Class to ingest event via HEC
    """

    def __init__(self, hec_uri, session_headers):
        """
        init method for the class

        Args:
            hec_uri(str): {splunk_hec_scheme}://{splunk_host}:{hec_port}/services/collector
            session_headers(dict): requesr header info.

            format::
                {
                    "Authorization": f"Splunk <hec-token>",
                }
        """
        self.hec_uri = hec_uri
        self.session_headers = session_headers

    def ingest(self, data):
        """
        Ingests event and metric data into splunk using HEC token via event endpoint.
        Args:
            data(dict): data dict with the info of the data to be ingested.

            format::
                {
                    "sourcetype": "sample_HEC",
                    "source": "sample_source",
                    "host": "sample_host",
                    "event": "event_str"
                }

            For batch ingestion of events in a single request at event endpoint provide a list of event dict to be ingested.
            format::
                [ 
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "event_str1"
                    },
                    {
                        "sourcetype": "sample_HEC",
                        "source": "sample_source",
                        "host": "sample_host",
                        "event": "metric"
                        "index": "metric_index"
                        "fields":{
                            "metric_name": "metric1",
                            "_value": 1,
                        }
                    }
                ]
        """
        try:
            response = requests.post(
                "{}/{}".format(self.hec_uri, "event"),
                auth=None,
                json=data,
                headers=self.session_headers,
                verify=False,
            )
            if response.status_code not in (200, 201):
                print(
                    "Status code: {} \nReason: {} \ntext:{}".format(
                        response.status_code, response.reason, response.text
                    )
                )
                raise Exception

        except Exception as e:
            print(e)
