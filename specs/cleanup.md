# Clean up the unnecessary files

**Objective** Your task is to cleanup the unnecessary code in the project that was built for legacy pipeline.

There are a few modules that is built for the new pipeline(yet to be streamlined) that we want to keep, rest of the code is redundant and need to be cleaned.

Pipeline files that we need to keep and should not be affected in the cleanup: - data_extraction_pipeline.py - demo_analysis_pipeline.py - founder_research_orchestrator.py - news_scrapper.py - prods_and_services.py - questionnaire_agent.py

Apart from the code that is not used in the above python files and it's depenendent files, you have to clean up the python modules inside src directory.

**Implementation details**

1. First analyse the files mentioned above and understand the code and packages dependent on these python modules
2. After that, come up with a list of files that are unnecessary and is not related to the main modules
