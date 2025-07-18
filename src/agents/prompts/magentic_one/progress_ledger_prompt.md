Recall we are working on the following request:

{task}

And we have assembled the following team:

{team}

To make progress on the request, please answer the following questions, including necessary reasoning:

    - Is the request fully satisfied? (True if complete or if there is NOT ENOUGH INFORMATION to proceed, False if the original request has yet to be SUCCESSFULLY addressed)
    - Are we in a loop where we are repeating a very similar requests and / or getting very similar responses as before?
      - Loops can span multiple turns, and can include repeated actions like requesting the same or very similar information in a row.
    - Are we making significant forward progress?
      - True if just starting, or recent messages are adding significant value.
      - False if recent messages show evidence of being stuck in a loop or if there is evidence of significant barriers to success such as the inability to read from a required file.
      - Be very strict, the analysis should be making significant progress, not just adding small bits of information.
    - Who should speak next? (select from: {team_names})
    - What instruction or question would you give this team member? (Phrase as if speaking directly to them, and include any specific information they may need)

It is possible that there is just not enough information available to continue the analysis. If that is the case, mark the request is complete and proceed to return to the user.

You should make narrow and specific requests. If you need to perform complex analysis, request it one step and one type of analysis at a time.
