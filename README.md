# TODO List
- Look into method for keeping all engines alive and retroactively setting the meta state values. We spend a lot of time in startups of the engines.
- Look into running games on demand. We currently wait for all to finish before starting / ending other games. We can speed that up maybe...
- Validate that the correct motions are assigned to the correct character pair!
- Further refine meta state ranges
- Add constraints for the meta state (G)
- Logging: Ensure log/engines/ is on the cluster's high-speed "scratch" storage, or the I/O might slow down your simulation.
- Chat said that the flop is that I do too many disk writes. I need to save things to a tmp folder then move it over when I am done. This is the disk on the node itself, and information doesn't have to travel over the network.
- Write small experiment to test the time difference between writing to tmp vs writing over cluster network
- Upgrade python on cluster bro
- I am so interested in jobs. I wanna learn how to create a space where I can submit jobs that require credits, and have cores / nodes just go and pick them up. Sounds so cool.
- You don't have to keep every motion file hey... If you have the gene that created that motion file, then theres no need.
- Additionally, we have motions and custom motions... We need to pick one!
- Add functionality to MCTS agents to perform only valid actions
- Look into saving tree results.
- Current MCTS agent cannot cancel actions mid action. IsControl flag will stop that.
- Current MCTS Still has some miss instances, need to diagnose that.
- We need look at adding match duration as another objective.
- We need to look into incorporating te passing of 50% into the entropy score
- Look into that normalization into the entropy term that chat said, dividing vy the Alduos
- Validate uniqueness working as expected... Single uniqueness runs don't maximize... thats weird!
- Look into improving MCTS by allowing opponent moves to be made as well as a separate branch... Right now, the opponent is kinda static.
- We need some identical gene culling. Maybe if you get identical genes in the nds, average their results or something
- Maybe look into removing elitism by replaying existing solutions, to remove luck based gameplay
- ✅ Correct the uniqueness constraint... Its looking at everything, which isnt fair. We need louder signals for things we actually control.
- ✅ When you look at solution replay, there is a lot of variance. We need to do experiments to find the optimal number of games to play to reduce that variance!!!
- ✅Look into using a Vectorized evaluation


# Note list
- N in MOEA is calculated as:
$$N = \binom{H + m - 1}{m - 1}$$
- Where H is n_partitions
- When running the code in a conda environment, you need to execute: conda install -c conda-forge openjdk=21.0.2. Need to figure out way to include this such that ita easy to start up
- We got 20 cores on my BBD laptop (might change when I move jobs)
- The harmonic mean calculation is:
$$\frac{n}{x_1^{-1}+\dots+x_n^{-1}} \quad s.t: 0\leq x_i \leq 1$$
- The function for the competitive balance is:
$$R(p)=e^{-\frac{(0.5-p)^2}{2\sigma^2}}$$
- We edited Zen and Garnet's default motion, because they had in build invalid motions! Cancellable motion level when the motion wasn't cancellable...

# Notes for Wednesday
- fixed comp balance because of degen strategy with Garnet
- Fixed comp balance calculation in the first place, so bad.
- Fixed uniqueness range.
- Data visualization
- - Add HV
- - Interactive 3D Scatter Plot
- - Parallel Coordinates Plot
- - Scatter Plot Matrix (Pairplots)

# NB NB Research Note
- by default, I have "removed" one of Garnets actions.
- that infinite combo was ruining the game, so I removed it

# Next Goals
- Research the variance.✅
- Maybe deterministic
- Check seeds as well✅
- Add visualization over run. ✅
- Really look into new method for defining uniqueness, we are just defining the genotype, and we need to measure the phenotype impact.
- Create MCTS agent that can play well. because we are currently not playing that well


# Notes for long jobs
- Please make sure that neutral has a cost of 0. This would kill some MCTS agent in some instances
