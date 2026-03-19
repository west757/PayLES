# PayLES - Program analyzing your Leave & Earnings Statement (LES)

**PayLES** is currently live at [payles.app](https://payles.app)!

**PayLES** (Program analyzing your Leave & Earnings Statement) is a free and open-source web application designed to help United States service members easily understand and manage their military finances. By uploading their monthly Leave and Earnings Statement (LES), users can quickly view a clear summary of their current pay and forecast their finances for the next 12 months. PayLES provides personalized insights and allows users to adjust future pay scenarios based on anticipated changes such as promotions, relocations, changes in dependents, tax status, and more. A Traditional Savings Plan (TSP) calculator is also available, aiding users in planning their pay allocations towards retirement. The platform is secure, user-friendly, and aims to empower service members to make informed financial decisions.

PayLES is designed to serve all Department of War service members, regardless of branch, component (Active Duty, Reserve, National Guard), rank, or job. It recognizes and incorporates service-specific pays, allowances, and deductions found in an LES, ensuring comprehensive coverage. The application aims to be a universal tool for analyzing military finances, adaptable to any service member's circumstances.

PayLES is intended solely for educational and budgeting purposes, helping service members analyze their current and future finances. The application is completely free, open source, and requires no advertisements, signups, or user accounts. All code and datasets are publicly available on GitHub.

For additional information, please visit the About & FAQ page at [payles.app/about_faq](https://payles.app/about_faq).

Please be aware, PayLES is currently in active development and frequent changes are being made that may impact existing functionality.

To contact the developer, please email: [payles.contact@pm.me](mailto:payles.contact@pm.me).

## License

This project is licensed under the MIT License.


<!--
Changes from Dev to Prod:
- main.py: comment out debug run, change to prod run
- config.py: update version date


short-term:
- oconus cola and oha calculations
- conus cola
- default for OCONUS locations in dropdown
- max TSP rate for specialty/incentive/bonus pay for roth tsp
- emergency fund goal calculator added to guide


mid-term:
- joint spouse with two LES
- hide drills row
- add pro-rated calculations for rows grade and zip code


long-term:
- leave calculator
- add comments and refactor code
- confirm carrying over debt to/from months on les (amount forward, carry forward)
- create unit tests 
- instructions for self-host
- reddit account
- merch (patch, coin)
- better css for border table scroll bar
- reports and graphs and pie chart


potential:
- rows displayed setting
- show custom rows setting
- import/export for custom rows
- add loading screen after submitting LES
- color code rows
- move branch into component
- minify style.css and script.js when pushed into a production environment


assistance needed:
- determining if a user is in a combat zone from their uploaded LES
- determining if a user is active duty or national guard/reserves from uploaded LES, and if so how many drills they've completed
- coast guard LES



Stationed Duty Location:

Country:
choose country

US:
enter zip code
if zip code alaska/hawaii, bring up locality dropdown
- displays zip code, tooltip is mha name

Non-US:
choose Locality
- displays locality code, tooltip is country - locality
enter rent
enter roommates

-->
