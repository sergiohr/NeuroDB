# NeuroDB

Los experimentos con registros neurofisiológicos multicanal generan gran volumen de información que debe ser obtenido y acumulado de manera simultánea en archivos sin estructura. Esto hace más costosa la ubicación, acceso y procesamiento de segmentos de interés luego de que el experimento ha finalizado. NeuroDB propone estructurar esta información en una base de datos relacional con una interfaz capaz de proporcionar alta disponibilidad y con respaldo de la información.

La estructura de la información esta basada en Neo (https://pythonhosted.org/neo/). Neo es un paquete de Python para la representación de información electrofisiológica.

El preprocesamiento de la señal, la adquisición de los spikes[1] y la clusterización de los mismos están basados en el trabajo de Quian Quiroga (http://papers.klab.caltech.edu/174/1/471.pdf‎), que a su vez utiliza una implementación del algoritmo Superparamagnetic de Blatt M., Wiseman S. y Domany E. (http://u.math.biu.ac.il/~louzouy/courses/seminar/magnet2.pdf‎). 

También se utiliza el método de clustering propuesto por Alejandro Laio en su trabajo "Clustering by fast search-and-find of density peaks" (http://people.sissa.it/~laio/Research/Res_clustering.php)

[1] Spikes: porción de señal donde se registro actividad debido a estimulo externo.

Para conocer más acerca de NeuroDB visitar la wiki del proyecto https://github.com/sergio2pi/NeuroDB/wiki
