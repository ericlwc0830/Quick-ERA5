# quick_era5 Documentation

## 基本介紹（Introduction）

這是一個用來快速下載與轉換ERA5資料的Python套件，可以利用它快速的下載ERA5的資料，並且將資料轉換成NetCDF、GeoTIFF等格式。

This is a Python package for quickly downloading and converting ERA5 data. You can use it to quickly download ERA5 data and convert it to formats such as NetCDF, GeoTIFF, etc.

## 資料來源（Data Source）

本套件使用的ERA5資料來源為google cloud storage所存放之公開資料集，詳細資訊請參考[ERA5 data on Google Cloud](https://cloud.google.com/storage/docs/public-datasets/era5)。

The ERA5 data used by this package is from the public dataset stored in google cloud storage. For more information, please refer to [ERA5 data on Google Cloud](https://cloud.google.com/storage/docs/public-datasets/era5).

## 如何安裝（Installation）

將quick_era5資料夾放到你的Python專案中，即可使用quick_era5套件，如下：

Put the quick_era5 folder in your Python project, and you can use the quick_era5 package as follows:


```python
from quick_era5 import era5_downloader, era5_converter
```

若你有專門用來放置Python套件的資料夾，可以將quick_era5資料夾放到該資料夾中，並且在Python程式中加入以下程式碼：

If you have a folder specifically for Python packages, you can put the quick_era5 folder in that folder and add the following code to your Python program:


```python
import sys
sys.path.append('path/to/quick_era5')

from quick_era5 import era5_downloader, era5_converter
```

## 依賴套件（Dependencies）

以下是quick_era5套件所直接引用的套件，括弧內為我測試時所使用的版本：

The following are the packages that the quick_era5 package depends on, with the version I used when testing in parentheses:

- affine (2.4.0)
- datetime
- gcsfs (2024.9.0post1)
- numpy (1.26.4)
- os
- pandas (2.2.2)
- pickle
- rasterio (1.4.1)
- xarray (2024.9.0)

## 如何下載ERA5資料（Downloading ERA5 Data）

先引用相關套件

First import the relevant packages


```python
import datetime
from quick_era5 import era5_downloader, era5_converter
```

接著即可指定資料進行下載，下載後將回傳一個xarray的資料集，如下：

Then you can specify the data for download. After downloading, an xarray dataset will be returned, as follows:

> 注意：下載的時間必須包含時區，避免下載到錯誤的資料。
> 
> Note: The download time must include the time zone to avoid downloading the wrong data.


```python
xarr = era5_downloader.download_era5_data_from_gcs(
    variable_list=['2m_temperature', 'geopotential'],
    from_datetime=datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc),  # 包含此時間（include）
    to_datetime=datetime.datetime(2020, 1, 2, tzinfo=datetime.timezone.utc),  # 包含此時間（include）
    time_interval=1,  # 以小時為單位（in hours）
)

xarr
```




<div><svg style="position: absolute; width: 0; height: 0; overflow: hidden">
<defs>
<symbol id="icon-database" viewBox="0 0 32 32">
<path d="M16 0c-8.837 0-16 2.239-16 5v4c0 2.761 7.163 5 16 5s16-2.239 16-5v-4c0-2.761-7.163-5-16-5z"></path>
<path d="M16 17c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
<path d="M16 26c-8.837 0-16-2.239-16-5v6c0 2.761 7.163 5 16 5s16-2.239 16-5v-6c0 2.761-7.163 5-16 5z"></path>
</symbol>
<symbol id="icon-file-text2" viewBox="0 0 32 32">
<path d="M28.681 7.159c-0.694-0.947-1.662-2.053-2.724-3.116s-2.169-2.030-3.116-2.724c-1.612-1.182-2.393-1.319-2.841-1.319h-15.5c-1.378 0-2.5 1.121-2.5 2.5v27c0 1.378 1.122 2.5 2.5 2.5h23c1.378 0 2.5-1.122 2.5-2.5v-19.5c0-0.448-0.137-1.23-1.319-2.841zM24.543 5.457c0.959 0.959 1.712 1.825 2.268 2.543h-4.811v-4.811c0.718 0.556 1.584 1.309 2.543 2.268zM28 29.5c0 0.271-0.229 0.5-0.5 0.5h-23c-0.271 0-0.5-0.229-0.5-0.5v-27c0-0.271 0.229-0.5 0.5-0.5 0 0 15.499-0 15.5 0v7c0 0.552 0.448 1 1 1h7v19.5z"></path>
<path d="M23 26h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 22h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
<path d="M23 18h-14c-0.552 0-1-0.448-1-1s0.448-1 1-1h14c0.552 0 1 0.448 1 1s-0.448 1-1 1z"></path>
</symbol>
</defs>
</svg>
<style>/* CSS stylesheet for displaying xarray objects in jupyterlab.
 *
 */

:root {
  --xr-font-color0: var(--jp-content-font-color0, rgba(0, 0, 0, 1));
  --xr-font-color2: var(--jp-content-font-color2, rgba(0, 0, 0, 0.54));
  --xr-font-color3: var(--jp-content-font-color3, rgba(0, 0, 0, 0.38));
  --xr-border-color: var(--jp-border-color2, #e0e0e0);
  --xr-disabled-color: var(--jp-layout-color3, #bdbdbd);
  --xr-background-color: var(--jp-layout-color0, white);
  --xr-background-color-row-even: var(--jp-layout-color1, white);
  --xr-background-color-row-odd: var(--jp-layout-color2, #eeeeee);
}

html[theme=dark],
html[data-theme=dark],
body[data-theme=dark],
body.vscode-dark {
  --xr-font-color0: rgba(255, 255, 255, 1);
  --xr-font-color2: rgba(255, 255, 255, 0.54);
  --xr-font-color3: rgba(255, 255, 255, 0.38);
  --xr-border-color: #1F1F1F;
  --xr-disabled-color: #515151;
  --xr-background-color: #111111;
  --xr-background-color-row-even: #111111;
  --xr-background-color-row-odd: #313131;
}

.xr-wrap {
  display: block !important;
  min-width: 300px;
  max-width: 700px;
}

.xr-text-repr-fallback {
  /* fallback to plain text repr when CSS is not injected (untrusted notebook) */
  display: none;
}

.xr-header {
  padding-top: 6px;
  padding-bottom: 6px;
  margin-bottom: 4px;
  border-bottom: solid 1px var(--xr-border-color);
}

.xr-header > div,
.xr-header > ul {
  display: inline;
  margin-top: 0;
  margin-bottom: 0;
}

.xr-obj-type,
.xr-array-name {
  margin-left: 2px;
  margin-right: 10px;
}

.xr-obj-type {
  color: var(--xr-font-color2);
}

.xr-sections {
  padding-left: 0 !important;
  display: grid;
  grid-template-columns: 150px auto auto 1fr 0 20px 0 20px;
}

.xr-section-item {
  display: contents;
}

.xr-section-item input {
  display: inline-block;
  opacity: 0;
}

.xr-section-item input + label {
  color: var(--xr-disabled-color);
}

.xr-section-item input:enabled + label {
  cursor: pointer;
  color: var(--xr-font-color2);
}

.xr-section-item input:focus + label {
  border: 2px solid var(--xr-font-color0);
}

.xr-section-item input:enabled + label:hover {
  color: var(--xr-font-color0);
}

.xr-section-summary {
  grid-column: 1;
  color: var(--xr-font-color2);
  font-weight: 500;
}

.xr-section-summary > span {
  display: inline-block;
  padding-left: 0.5em;
}

.xr-section-summary-in:disabled + label {
  color: var(--xr-font-color2);
}

.xr-section-summary-in + label:before {
  display: inline-block;
  content: '►';
  font-size: 11px;
  width: 15px;
  text-align: center;
}

.xr-section-summary-in:disabled + label:before {
  color: var(--xr-disabled-color);
}

.xr-section-summary-in:checked + label:before {
  content: '▼';
}

.xr-section-summary-in:checked + label > span {
  display: none;
}

.xr-section-summary,
.xr-section-inline-details {
  padding-top: 4px;
  padding-bottom: 4px;
}

.xr-section-inline-details {
  grid-column: 2 / -1;
}

.xr-section-details {
  display: none;
  grid-column: 1 / -1;
  margin-bottom: 5px;
}

.xr-section-summary-in:checked ~ .xr-section-details {
  display: contents;
}

.xr-array-wrap {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 20px auto;
}

.xr-array-wrap > label {
  grid-column: 1;
  vertical-align: top;
}

.xr-preview {
  color: var(--xr-font-color3);
}

.xr-array-preview,
.xr-array-data {
  padding: 0 5px !important;
  grid-column: 2;
}

.xr-array-data,
.xr-array-in:checked ~ .xr-array-preview {
  display: none;
}

.xr-array-in:checked ~ .xr-array-data,
.xr-array-preview {
  display: inline-block;
}

.xr-dim-list {
  display: inline-block !important;
  list-style: none;
  padding: 0 !important;
  margin: 0;
}

.xr-dim-list li {
  display: inline-block;
  padding: 0;
  margin: 0;
}

.xr-dim-list:before {
  content: '(';
}

.xr-dim-list:after {
  content: ')';
}

.xr-dim-list li:not(:last-child):after {
  content: ',';
  padding-right: 5px;
}

.xr-has-index {
  font-weight: bold;
}

.xr-var-list,
.xr-var-item {
  display: contents;
}

.xr-var-item > div,
.xr-var-item label,
.xr-var-item > .xr-var-name span {
  background-color: var(--xr-background-color-row-even);
  margin-bottom: 0;
}

.xr-var-item > .xr-var-name:hover span {
  padding-right: 5px;
}

.xr-var-list > li:nth-child(odd) > div,
.xr-var-list > li:nth-child(odd) > label,
.xr-var-list > li:nth-child(odd) > .xr-var-name span {
  background-color: var(--xr-background-color-row-odd);
}

.xr-var-name {
  grid-column: 1;
}

.xr-var-dims {
  grid-column: 2;
}

.xr-var-dtype {
  grid-column: 3;
  text-align: right;
  color: var(--xr-font-color2);
}

.xr-var-preview {
  grid-column: 4;
}

.xr-index-preview {
  grid-column: 2 / 5;
  color: var(--xr-font-color2);
}

.xr-var-name,
.xr-var-dims,
.xr-var-dtype,
.xr-preview,
.xr-attrs dt {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 10px;
}

.xr-var-name:hover,
.xr-var-dims:hover,
.xr-var-dtype:hover,
.xr-attrs dt:hover {
  overflow: visible;
  width: auto;
  z-index: 1;
}

.xr-var-attrs,
.xr-var-data,
.xr-index-data {
  display: none;
  background-color: var(--xr-background-color) !important;
  padding-bottom: 5px !important;
}

.xr-var-attrs-in:checked ~ .xr-var-attrs,
.xr-var-data-in:checked ~ .xr-var-data,
.xr-index-data-in:checked ~ .xr-index-data {
  display: block;
}

.xr-var-data > table {
  float: right;
}

.xr-var-name span,
.xr-var-data,
.xr-index-name div,
.xr-index-data,
.xr-attrs {
  padding-left: 25px !important;
}

.xr-attrs,
.xr-var-attrs,
.xr-var-data,
.xr-index-data {
  grid-column: 1 / -1;
}

dl.xr-attrs {
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 125px auto;
}

.xr-attrs dt,
.xr-attrs dd {
  padding: 0;
  margin: 0;
  float: left;
  padding-right: 10px;
  width: auto;
}

.xr-attrs dt {
  font-weight: normal;
  grid-column: 1;
}

.xr-attrs dt:hover span {
  display: inline-block;
  background: var(--xr-background-color);
  padding-right: 10px;
}

.xr-attrs dd {
  grid-column: 2;
  white-space: pre-wrap;
  word-break: break-all;
}

.xr-icon-database,
.xr-icon-file-text2,
.xr-no-icon {
  display: inline-block;
  vertical-align: middle;
  width: 1em;
  height: 1.5em !important;
  stroke-width: 0;
  stroke: currentColor;
  fill: currentColor;
}
</style><pre class='xr-text-repr-fallback'>&lt;xarray.Dataset&gt; Size: 4GB
Dimensions:         (time: 25, latitude: 721, longitude: 1440, level: 37)
Coordinates:
  * latitude        (latitude) float32 3kB 90.0 89.75 89.5 ... -89.75 -90.0
  * level           (level) int64 296B 1 2 3 5 7 10 ... 875 900 925 950 975 1000
  * longitude       (longitude) float32 6kB 0.0 0.25 0.5 ... 359.2 359.5 359.8
  * time            (time) datetime64[ns] 200B 2020-01-01 ... 2020-01-02
Data variables:
    2m_temperature  (time, latitude, longitude) float32 104MB ...
    geopotential    (time, level, latitude, longitude) float32 4GB ...
Attributes:
    valid_time_start:  1940-01-01
    last_updated:      2024-10-17 20:04:10.783634
    valid_time_stop:   2024-07-31</pre><div class='xr-wrap' style='display:none'><div class='xr-header'><div class='xr-obj-type'>xarray.Dataset</div></div><ul class='xr-sections'><li class='xr-section-item'><input id='section-7dce92d2-34ce-4798-b957-fe3aafba9b47' class='xr-section-summary-in' type='checkbox' disabled ><label for='section-7dce92d2-34ce-4798-b957-fe3aafba9b47' class='xr-section-summary'  title='Expand/collapse section'>Dimensions:</label><div class='xr-section-inline-details'><ul class='xr-dim-list'><li><span class='xr-has-index'>time</span>: 25</li><li><span class='xr-has-index'>latitude</span>: 721</li><li><span class='xr-has-index'>longitude</span>: 1440</li><li><span class='xr-has-index'>level</span>: 37</li></ul></div><div class='xr-section-details'></div></li><li class='xr-section-item'><input id='section-8ed344d2-6ec9-4fe3-9ac7-e3fe22d5948b' class='xr-section-summary-in' type='checkbox'  checked><label for='section-8ed344d2-6ec9-4fe3-9ac7-e3fe22d5948b' class='xr-section-summary' >Coordinates: <span>(4)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>latitude</span></div><div class='xr-var-dims'>(latitude)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>90.0 89.75 89.5 ... -89.75 -90.0</div><input id='attrs-07743e61-c164-45d3-8f53-a3093dbb5ced' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-07743e61-c164-45d3-8f53-a3093dbb5ced' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-5fbdcdd9-9b6c-4a19-8bc4-caa04326569b' class='xr-var-data-in' type='checkbox'><label for='data-5fbdcdd9-9b6c-4a19-8bc4-caa04326569b' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>latitude</dd><dt><span>units :</span></dt><dd>degrees_north</dd></dl></div><div class='xr-var-data'><pre>array([ 90.  ,  89.75,  89.5 , ..., -89.5 , -89.75, -90.  ], dtype=float32)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>level</span></div><div class='xr-var-dims'>(level)</div><div class='xr-var-dtype'>int64</div><div class='xr-var-preview xr-preview'>1 2 3 5 7 ... 900 925 950 975 1000</div><input id='attrs-f4bc1481-efd9-4715-8953-e6d110fc4b99' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-f4bc1481-efd9-4715-8953-e6d110fc4b99' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-4fdbb85c-669f-42cd-89af-16e363dd5e58' class='xr-var-data-in' type='checkbox'><label for='data-4fdbb85c-669f-42cd-89af-16e363dd5e58' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([   1,    2,    3,    5,    7,   10,   20,   30,   50,   70,  100,  125,
        150,  175,  200,  225,  250,  300,  350,  400,  450,  500,  550,  600,
        650,  700,  750,  775,  800,  825,  850,  875,  900,  925,  950,  975,
       1000])</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>longitude</span></div><div class='xr-var-dims'>(longitude)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>0.0 0.25 0.5 ... 359.2 359.5 359.8</div><input id='attrs-ff4896fc-a333-467a-aa6b-37fe75b95d3e' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-ff4896fc-a333-467a-aa6b-37fe75b95d3e' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-13e32639-4059-45a1-8d34-bdb19bf179c6' class='xr-var-data-in' type='checkbox'><label for='data-13e32639-4059-45a1-8d34-bdb19bf179c6' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>longitude</dd><dt><span>units :</span></dt><dd>degrees_east</dd></dl></div><div class='xr-var-data'><pre>array([0.0000e+00, 2.5000e-01, 5.0000e-01, ..., 3.5925e+02, 3.5950e+02,
       3.5975e+02], dtype=float32)</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span class='xr-has-index'>time</span></div><div class='xr-var-dims'>(time)</div><div class='xr-var-dtype'>datetime64[ns]</div><div class='xr-var-preview xr-preview'>2020-01-01 ... 2020-01-02</div><input id='attrs-3166e622-5730-41af-a303-55dbd315366b' class='xr-var-attrs-in' type='checkbox' disabled><label for='attrs-3166e622-5730-41af-a303-55dbd315366b' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-83d0ed6b-24c1-428d-ab11-eca7c6f3c6e7' class='xr-var-data-in' type='checkbox'><label for='data-83d0ed6b-24c1-428d-ab11-eca7c6f3c6e7' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'></dl></div><div class='xr-var-data'><pre>array([&#x27;2020-01-01T00:00:00.000000000&#x27;, &#x27;2020-01-01T01:00:00.000000000&#x27;,
       &#x27;2020-01-01T02:00:00.000000000&#x27;, &#x27;2020-01-01T03:00:00.000000000&#x27;,
       &#x27;2020-01-01T04:00:00.000000000&#x27;, &#x27;2020-01-01T05:00:00.000000000&#x27;,
       &#x27;2020-01-01T06:00:00.000000000&#x27;, &#x27;2020-01-01T07:00:00.000000000&#x27;,
       &#x27;2020-01-01T08:00:00.000000000&#x27;, &#x27;2020-01-01T09:00:00.000000000&#x27;,
       &#x27;2020-01-01T10:00:00.000000000&#x27;, &#x27;2020-01-01T11:00:00.000000000&#x27;,
       &#x27;2020-01-01T12:00:00.000000000&#x27;, &#x27;2020-01-01T13:00:00.000000000&#x27;,
       &#x27;2020-01-01T14:00:00.000000000&#x27;, &#x27;2020-01-01T15:00:00.000000000&#x27;,
       &#x27;2020-01-01T16:00:00.000000000&#x27;, &#x27;2020-01-01T17:00:00.000000000&#x27;,
       &#x27;2020-01-01T18:00:00.000000000&#x27;, &#x27;2020-01-01T19:00:00.000000000&#x27;,
       &#x27;2020-01-01T20:00:00.000000000&#x27;, &#x27;2020-01-01T21:00:00.000000000&#x27;,
       &#x27;2020-01-01T22:00:00.000000000&#x27;, &#x27;2020-01-01T23:00:00.000000000&#x27;,
       &#x27;2020-01-02T00:00:00.000000000&#x27;], dtype=&#x27;datetime64[ns]&#x27;)</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-2e9137ec-606f-4836-b839-c6cddadd2ab8' class='xr-section-summary-in' type='checkbox'  checked><label for='section-2e9137ec-606f-4836-b839-c6cddadd2ab8' class='xr-section-summary' >Data variables: <span>(2)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-var-name'><span>2m_temperature</span></div><div class='xr-var-dims'>(time, latitude, longitude)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-24c44ad6-7461-43e3-acee-55e220bb769d' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-24c44ad6-7461-43e3-acee-55e220bb769d' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-e7b69a20-dd74-477e-8394-6b30b28f372e' class='xr-var-data-in' type='checkbox'><label for='data-e7b69a20-dd74-477e-8394-6b30b28f372e' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>2 metre temperature</dd><dt><span>short_name :</span></dt><dd>t2m</dd><dt><span>units :</span></dt><dd>K</dd></dl></div><div class='xr-var-data'><pre>[25956000 values with dtype=float32]</pre></div></li><li class='xr-var-item'><div class='xr-var-name'><span>geopotential</span></div><div class='xr-var-dims'>(time, level, latitude, longitude)</div><div class='xr-var-dtype'>float32</div><div class='xr-var-preview xr-preview'>...</div><input id='attrs-3db8273f-a8db-4d2f-92c9-e6d85b0a4b9c' class='xr-var-attrs-in' type='checkbox' ><label for='attrs-3db8273f-a8db-4d2f-92c9-e6d85b0a4b9c' title='Show/Hide attributes'><svg class='icon xr-icon-file-text2'><use xlink:href='#icon-file-text2'></use></svg></label><input id='data-ac8c8620-6096-424f-a1ad-88b737f5b422' class='xr-var-data-in' type='checkbox'><label for='data-ac8c8620-6096-424f-a1ad-88b737f5b422' title='Show/Hide data repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-var-attrs'><dl class='xr-attrs'><dt><span>long_name :</span></dt><dd>Geopotential</dd><dt><span>short_name :</span></dt><dd>z</dd><dt><span>standard_name :</span></dt><dd>geopotential</dd><dt><span>units :</span></dt><dd>m**2 s**-2</dd></dl></div><div class='xr-var-data'><pre>[960372000 values with dtype=float32]</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-b66d98f2-af12-42eb-8826-300ee8653e60' class='xr-section-summary-in' type='checkbox'  ><label for='section-b66d98f2-af12-42eb-8826-300ee8653e60' class='xr-section-summary' >Indexes: <span>(4)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><ul class='xr-var-list'><li class='xr-var-item'><div class='xr-index-name'><div>latitude</div></div><div class='xr-index-preview'>PandasIndex</div><div></div><input id='index-2d29cbf4-3963-4c34-be5f-289d3784913e' class='xr-index-data-in' type='checkbox'/><label for='index-2d29cbf4-3963-4c34-be5f-289d3784913e' title='Show/Hide index repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-index-data'><pre>PandasIndex(Index([  90.0,  89.75,   89.5,  89.25,   89.0,  88.75,   88.5,  88.25,   88.0,
        87.75,
       ...
       -87.75,  -88.0, -88.25,  -88.5, -88.75,  -89.0, -89.25,  -89.5, -89.75,
        -90.0],
      dtype=&#x27;float32&#x27;, name=&#x27;latitude&#x27;, length=721))</pre></div></li><li class='xr-var-item'><div class='xr-index-name'><div>level</div></div><div class='xr-index-preview'>PandasIndex</div><div></div><input id='index-b1b720a1-cf0f-466d-82fc-e1ab9ba99635' class='xr-index-data-in' type='checkbox'/><label for='index-b1b720a1-cf0f-466d-82fc-e1ab9ba99635' title='Show/Hide index repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-index-data'><pre>PandasIndex(Index([   1,    2,    3,    5,    7,   10,   20,   30,   50,   70,  100,  125,
        150,  175,  200,  225,  250,  300,  350,  400,  450,  500,  550,  600,
        650,  700,  750,  775,  800,  825,  850,  875,  900,  925,  950,  975,
       1000],
      dtype=&#x27;int64&#x27;, name=&#x27;level&#x27;))</pre></div></li><li class='xr-var-item'><div class='xr-index-name'><div>longitude</div></div><div class='xr-index-preview'>PandasIndex</div><div></div><input id='index-22dbf9a1-a6fc-4d72-9baf-ccbe20b9f923' class='xr-index-data-in' type='checkbox'/><label for='index-22dbf9a1-a6fc-4d72-9baf-ccbe20b9f923' title='Show/Hide index repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-index-data'><pre>PandasIndex(Index([   0.0,   0.25,    0.5,   0.75,    1.0,   1.25,    1.5,   1.75,    2.0,
         2.25,
       ...
        357.5, 357.75,  358.0, 358.25,  358.5, 358.75,  359.0, 359.25,  359.5,
       359.75],
      dtype=&#x27;float32&#x27;, name=&#x27;longitude&#x27;, length=1440))</pre></div></li><li class='xr-var-item'><div class='xr-index-name'><div>time</div></div><div class='xr-index-preview'>PandasIndex</div><div></div><input id='index-1181b1ca-8529-4699-9e84-fd40b6a952ea' class='xr-index-data-in' type='checkbox'/><label for='index-1181b1ca-8529-4699-9e84-fd40b6a952ea' title='Show/Hide index repr'><svg class='icon xr-icon-database'><use xlink:href='#icon-database'></use></svg></label><div class='xr-index-data'><pre>PandasIndex(DatetimeIndex([&#x27;2020-01-01 00:00:00&#x27;, &#x27;2020-01-01 01:00:00&#x27;,
               &#x27;2020-01-01 02:00:00&#x27;, &#x27;2020-01-01 03:00:00&#x27;,
               &#x27;2020-01-01 04:00:00&#x27;, &#x27;2020-01-01 05:00:00&#x27;,
               &#x27;2020-01-01 06:00:00&#x27;, &#x27;2020-01-01 07:00:00&#x27;,
               &#x27;2020-01-01 08:00:00&#x27;, &#x27;2020-01-01 09:00:00&#x27;,
               &#x27;2020-01-01 10:00:00&#x27;, &#x27;2020-01-01 11:00:00&#x27;,
               &#x27;2020-01-01 12:00:00&#x27;, &#x27;2020-01-01 13:00:00&#x27;,
               &#x27;2020-01-01 14:00:00&#x27;, &#x27;2020-01-01 15:00:00&#x27;,
               &#x27;2020-01-01 16:00:00&#x27;, &#x27;2020-01-01 17:00:00&#x27;,
               &#x27;2020-01-01 18:00:00&#x27;, &#x27;2020-01-01 19:00:00&#x27;,
               &#x27;2020-01-01 20:00:00&#x27;, &#x27;2020-01-01 21:00:00&#x27;,
               &#x27;2020-01-01 22:00:00&#x27;, &#x27;2020-01-01 23:00:00&#x27;,
               &#x27;2020-01-02 00:00:00&#x27;],
              dtype=&#x27;datetime64[ns]&#x27;, name=&#x27;time&#x27;, freq=None))</pre></div></li></ul></div></li><li class='xr-section-item'><input id='section-a66979c5-42be-447f-8f13-a91566a719da' class='xr-section-summary-in' type='checkbox'  checked><label for='section-a66979c5-42be-447f-8f13-a91566a719da' class='xr-section-summary' >Attributes: <span>(3)</span></label><div class='xr-section-inline-details'></div><div class='xr-section-details'><dl class='xr-attrs'><dt><span>valid_time_start :</span></dt><dd>1940-01-01</dd><dt><span>last_updated :</span></dt><dd>2024-10-17 20:04:10.783634</dd><dt><span>valid_time_stop :</span></dt><dd>2024-07-31</dd></dl></div></li></ul></div></div>



資料下載後，將會存放在快取資料夾內，以便下次快速存取，不過預設僅會保存14天，超過後將會於下次執行下載時自動刪除。若要調整快取檔案的存放期限，可以自行調整，如下：

After the data is downloaded, it will be stored in the cache folder for quick access next time. However, it will only be saved for 14 days by default. If it exceeds this period, it will be automatically deleted the next time it is downloaded. If you want to adjust the storage period of the cache file, you can adjust it yourself, as follows:


```python
# 一天後刪除cache
# Delete cache after 1 day
era5_downloader.expire_days = 1
```

## 將xarray資料集進行轉換（Converting xarray Dataset）

### 轉換成NetCDF檔案（Convert to NetCDF File）

若要將xarray的資料集轉換成NetCDF檔案，可以使用以下程式碼：

If you want to convert the xarray dataset to a NetCDF file, you can use the following code:


```python
xarr = xarr
save_at = 'output.nc'
era5_converter.era5_xarray_to_netcdf(xarr=xarr, save_at=save_at)
```

### 將xarray資料集轉換成GeoTIFF檔案（Convert xarray Dataset to GeoTIFF File）

若要將指定變數、高度、時間的xarray的資料集轉換成GeoTIFF檔案，可以使用以下程式碼：

If you want to convert the xarray dataset with specified variables, heights, and times to a GeoTIFF file, you can use the following code:


```python
# 當變數只有一個高度時，z設為None
# When the variable has only one height, set z to None
xarr = xarr
variable = '2m_temperature'
z = None 
time = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)
save_at = 'output_2m_temperature.tif'
era5_converter.era5_xarray_to_geotiff(xarr=xarr, variable=variable, z=z, time=time, save_at=save_at)


# 當變數包含多種高度時，z設為要的高度
# When the variable has multiple heights, set z to the desired height
xarr = xarr
variable = '2m_temperature'
z = None 
time = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)
save_at = 'output_2m_temperature.tif'
era5_converter.era5_xarray_to_geotiff(xarr=xarr, variable=variable, z=z, time=time, save_at=save_at)
```

### 將xarray資料集轉換成numpy陣列（Convert xarray Dataset to Numpy Array）   

若要將xarray的資料集轉換成numpy陣列，可以使用以下程式碼：

If you want to convert the xarray dataset to a numpy array, you can use the following code:


```python
xarr = xarr
variable = '2m_temperature'
z = None
time = datetime.datetime(2020, 1, 1, 12, tzinfo=datetime.timezone.utc)
arr = era5_converter.era5_xarray_to_nparray(xarr=xarr, variable=variable, z=z, time=time)
```

以下程式碼示範如何快速繪製該numpy陣列：

The following code demonstrates how to quickly plot the numpy array:


```python
from matplotlib import pyplot as plt
plt.imshow(arr)
```




    <matplotlib.image.AxesImage at 0x1681742b0>




    
![png](readme_files/readme_18_1.png)
    


## 完整說明文件

### era5_downloader 設定

#### era5_gcp_path

此設定值用來指定ERA5資料在GCS中的路徑，預設為`gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`。

#### expire_days

此設定值用來指定快取檔案的存放期限，預設為14天。

### era5_downloader 函數

#### download_era5_data_from_gcs

下載GCS中的ERA5資料，並回傳xarray資料集。


參數：
- variable_list: list, 要下載的變數列表。
- from_date: datetime.datetime, 資料的起始時間。
- to_date: datetime.datetime, 資料的結束時間（包含此時間）。
- data_steps: int, 每筆資料之間的時間間隔。

回傳：
- xarray.Dataset, 下載的ERA5資料集。


#### show_era5_variables

顯示ERA5資料集中的氣象變數。

參數：
- 無

回傳：
- list, ERA5資料集中的氣象變數列表。

### era5_converter 函數

#### convert_xarray_to_netcdf

將xarray資料集存成NetCDF檔案。

參數：
- xarr: xarray.core.dataset.Dataset, 要存的xarray資料集。
- file_path: str, 要存的檔案路徑。

回傳：
- None

#### convert_xarray_to_geotiff

將xarray資料集中指定的變數、高度、時間資料存成GeoTIFF檔案。

參數：
- xarr: xarray.core.dataset.Dataset, 要存的xarray資料集。
- variable: str, 要存的變數。
- z: int or float or None, 要存的高度，若資料只有一個高度，請使用None。
- time: datetime.datetime, 要存的時間，若時區為None，將會轉換成UTC。
- save_at: str, 要存的GeoTIFF檔案路徑。

回傳：
- None

#### convert_xarray_to_numpy_array

將xarray資料集中指定的變數、高度、時間資料存成numpy陣列。

參數：
- xarr: xarray.core.dataset.Dataset, 要存的xarray資料集。
- variable: str, 要存的變數。
- z: int or float or None, 要存的高度，若資料只有一個高度，請使用None。
- time: datetime.datetime, 要存的時間，若時區為None，將會轉換成UTC。

回傳：
- np.ndarray, 指定變數、高度、時間資料的numpy陣列。

## Full Documentation

### era5_downloader settings

#### era5_gcp_path

This setting value is used to specify the path of ERA5 data in GCS, and the default value is `gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3`.

#### expire_days

This setting value is used to specify the storage period of the cache file, and the default value is 14 days.

### era5_downloader functions

#### download_era5_data_from_gcs

Download the era5 data from GCS and return the xarray dataset.

Args:
- variable_list: list, list of variables to download.
- from_date: datetime.datetime, start datetime of the data.
- to_date: datetime.datetime, end datetime (include this datetime) of the data.
- data_steps: int, hours between each data.

Returns:
- xarray.Dataset, the era5 dataset.

#### show_era5_variables

Show the variables in the era5 dataset.

Args:
- None
    
Returns:
- list, list of variables in the era5 dataset.

### era5_converter functions

#### convert_xarray_to_netcdf

Save the xarray dataset to a netcdf file.

Args:
- xarr, xarray.core.dataset.Dataset, the xarray dataset to save.
- file_path, str, the file path to save the xarray dataset.

Returns:
- None

#### convert_xarray_to_geotiff

Save the specified variable, pressure level, time data in the xarray dataset to a geotiff file.

Args:
- xarr: xarray.core.dataset.Dataset, the xarray dataset to save.
- variable: str, the variable to save.
- z: int or float or None, the z level to save, if data has only one level, use None.
- time: datetime.datetime, the time to save, if timezone is None, it will be converted to UTC.
- save_at: str, the file path to save geotiff file.

Returns:
- None

#### convert_xarray_to_numpy_array

Save the specified variable, pressure level, time data in the xarray dataset to a numpy array.

Args:
- xarr: xarray.core.dataset.Dataset, the xarray dataset to save.
- variable: str, the variable to save.
- z: int or float or None, the z level to save, if data has only one level, use None.
- time: datetime.datetime, the time to save, if timezone is None, it will be converted to UTC.

Returns:
- np.ndarray, the numpy array of the specified variable, pressure level, time data.


