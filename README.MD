# Skimmer using CRAB3

## For data, use:

```bash crab_submission.sh```

This will submit CRAB jobs for Data using the config file ```crab_cfg.py```, with the executable ```crab_script.py```, pset file ```PSet.py``` and bash script for crab nodes - ```crab_script.sh```. The datasets are populated in ```datsets.txt```


## For MC, use:

```bash crab_submission_sequential.sh``` 
This will submit CRAB jobs for Data using the config file ```crab_cfg_sequential.py```, with the executable ```crab_script.py```, pset file ```PSet.py``` and bash script for crab nodes - ```crab_script.sh```. The datasets are populated in ```datsets_MC.txt```