from prometheus_client import Counter

TRACKS_SENT = Counter('tracks_sent_total', 'Total number of tracks sent', ['playlist'])
