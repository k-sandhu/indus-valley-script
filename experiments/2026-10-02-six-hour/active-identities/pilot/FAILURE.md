# Pilot serialization failure

The first pilot computed twelve conditions and then failed while serializing its mechanism checks. A NumPy Boolean from the normalization comparison was passed directly to JSON. The standard serializer rejected it, leaving no saved trial result. The failed code snapshot and this endpoint are preserved. The repair converts check values to ordinary Python Booleans and writes the completed JSON string before creating its destination directory. The next pilot uses a fresh endpoint.
