#!/bin/bash
swagger-codegen generate -i controller.yaml -l python -o client -DpackageName=controller
#swagger-codegen generate -i controller.yaml -l python-flask -o server
cd client
pip3 uninstall controller
python3 setup.py install