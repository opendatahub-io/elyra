#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <NEW_VERSION>"
  exit 1
fi

NEW_VERSION=$1

echo "Updating version in UI packages ..."
npx lerna@8.1.8 version "$NEW_VERSION" --no-git-tag-version --no-push --yes

echo "Formatting files ..."
make prettier-ui

echo "Updating version in elyra/_version.py ..."
sed -i.bak "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" elyra/_version.py && rm elyra/_version.py.bak

echo "Version successfully updated to $NEW_VERSION"
