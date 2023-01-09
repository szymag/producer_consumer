[![CircleCI](https://circleci.com/gh/szymag/producer_consumer.svg?style=shield)](https://circleci.com/gh/szymag/producer_consumer)


## Producer - consumer problem for picture manipulation
The `Producer` thread receives data from `Source` and passes to `queue A` that is shared with `Consumer`. `Consumer` process data, i.e., resize and apply median filter and then pass to another `queue B`. From `queue B`, thread `SavePicture` take data and save it to a png file.
This architecture has 3 levels, where the middle one is both producer and consumer.

All threads run simultaneously, and `join()` is executed after starting all threads. This speeds up work and data are continuously taken from pipelines. However, it complicates the condition to stop threads of the consumer. 
Here, information about the amount of data (variable named `frame_count`) is explicitly passed to all threads. It must be assured that all threads take the same values. 