import 'vtk.js/Sources/favicon';

import macro from 'vtk.js/Sources/macro';
import DataAccessHelper from 'vtk.js/Sources/IO/Core/DataAccessHelper';
import HttpDataAccessHelper from 'vtk.js/Sources/IO/Core/DataAccessHelper/HttpDataAccessHelper';
import vtkFullScreenRenderWindow from 'vtk.js/Sources/Rendering/Misc/FullScreenRenderWindow';
import vtkHttpSceneLoader from 'vtk.js/Sources/IO/Core/HttpSceneLoader';
import vtkURLExtract from 'vtk.js/Sources/Common/Core/URLExtract';

import controlWidget from './SceneExplorerWidget';
import style from './SceneExplorer.module.css';

console.log("index.js: loaded");