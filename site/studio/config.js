/* Studio FGA: where the Studio API lives. The only setting the page has.

   After the owner deploys the backend (studio/server/README.md, "Deploy"), Modal prints the web address, like
   https://<workspace>--studio-fga-web.modal.run . Put that address here (no slash at the end), commit, and the
   page starts using it. Until then the page still works: "Start free" opens the demo with the sample project
   (?demo=1), which never calls the API. */
window.STUDIO_API = "https://akshatpagariya909--studio-fga-web.us-east.modal.run";
