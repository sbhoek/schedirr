# schedirr
Python package that can do calculations needed for the scheduling of irrigation in tertiary units

![20220906_120140_warped](https://github.com/sbhoek/schedirr/assets/505271/befd5a57-c1fa-4ed3-8048-75b27ddaf58f)

The model that forms the basis for this package is basically a water balance model: not for one field but for a tertiary unit or an irrigated area downstream of a storage reservoir. It is assumed that the irrigated area is so large that not all fields can be sown / planted at the same time. This is often the case when rice is one of the important crops and the soil allows puddling - a special way to do land preparation. The initial water gift that is needed before the puddling work can start - together with the available canal capacity - often forms a bottleneck. The time needed to have all fields in the irrigated area sown / planted, is referred to as spreading period. The model helps to estimate what average water depth is needed in every period - usu. in every month - based on the water requirements of a single field during various stages (input). The estimates are basically obtained by means of a kind of convolution process.
