# graphene-protobuf
Testing graphql query resolving off protobuf

# Install
`pip install graphene protobuf`

# Run

`./hello.py`

# To recompile your .proto definition
Just pre-compiled for linux x86_64 [here](https://github.com/protocolbuffers/protobuf/releases/tag/v3.7.0)

Or `sudo apt-get install protobuf-compiler`

Then from the clone:
```
$ protoc -I=./ --python_out=./ hello.proto
```

