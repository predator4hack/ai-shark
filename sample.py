from runner import productAndServicesAnalyser

if __name__ == "__main__":
    # ✅ Replace this URL with any domain you want to test
    domain = "https://www.loophealth.com/"

    print(f"Starting Product & Services Analysis for {domain}...\n")
    
    report = productAndServicesAnalyser(domain)

    print("\n🎯 Analysis complete. Summary:")
    for section, values in report.items():
        print(f"\n## {section.replace('_',' ').title()}")
        for k, v in values.items():
            print(f"- {k}: {v if v else 'N/A'}")
