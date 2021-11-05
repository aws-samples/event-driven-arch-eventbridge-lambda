#!/bin/bash
for i in {1..100}; do cp valido.xml "valido-$i.xml"; done
for i in {1..100}; do cp invalido.xml "invalido-$i.xml"; done