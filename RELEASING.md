# Releasing the AfBo CLDF dataset

- Re-create the CLDF dataset running

  ```shell
  cldfbench makecldf cldfbench_afbo.py --glottolog-version v5.3 --with-cldfreadme --with-zenodo
  cldfbench readme cldfbench_afbo.py
  ```

- Make sure the data is valid running

  ```shell
  pip install pytest-cldf
  pytest
  cldf validate cldf --with-cldf-markdown
  ```

- Commit all changes, tag the release, push code and tags
- Create a release on GitHub and make sure it is picked up by Zenodo
