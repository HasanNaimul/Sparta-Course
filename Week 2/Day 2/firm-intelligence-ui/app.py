import httpx
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Firm Intelligence", page_icon="🤖")
st.title("Firm Intelligence")


# ---------------- ASK AGENT ----------------

st.header("Ask the Agent")

question = st.text_input(
    "Your question",
    placeholder="How is profit per equity partner calculated?"
)

if st.button("Ask Agent"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            response = httpx.post(
                f"{API_BASE}/agent/ask",
                json={"question": question},
                timeout=60.0,
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("completed"):
                    st.markdown(data["answer"])
                else:
                    st.warning("The agent did not complete the request.")

                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "Tool calls",
                    data.get("tool_calls_made", 0)
                )

                col2.metric(
                    "Input tokens",
                    data.get("input_tokens", 0)
                )

                col3.metric(
                    "Output tokens",
                    data.get("output_tokens", 0)
                )

            elif response.status_code == 504:
                st.error("The AI provider timed out.")

            elif response.status_code == 429:
                st.error("The AI provider is rate limited.")

            elif response.status_code == 502:
                st.error("The AI provider is unavailable.")

            else:
                st.error(
                    f"Request failed: HTTP {response.status_code}"
                )

        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")


# ---------------- SEARCH ----------------

st.divider()
st.header("Search Knowledge Base")

search_question = st.text_input(
    "Search query",
    key="search"
)

top_k = st.slider(
    "Number of results",
    1,
    8,
    3
)

if st.button("Search"):

    if not search_question.strip():
        st.warning("Please enter a search query.")

    else:
        try:
            response = httpx.post(
                f"{API_BASE}/knowledge/search",
                json={
                    "question": search_question,
                    "top_k": top_k
                },
                timeout=30.0,
            )

            if response.status_code == 200:
                results = response.json().get("results", [])

                if not results:
                    st.info("No results found.")

                for result in results:
                    st.subheader(result["title"])
                    st.write(
                        f"Score: {result['score']:.3f}"
                    )

                    with st.expander("Show document"):
                        st.write(result["text"])

            elif response.status_code == 503:
                st.warning(
                    "The knowledge index has not been built yet."
                )

            else:
                st.error(
                    f"Search failed: HTTP {response.status_code}"
                )

        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")


# ---------------- STREAMING SUMMARY ----------------

st.divider()
st.header("Streaming Firm Summary")

try:
    response = httpx.get(
        f"{API_BASE}/firms",
        timeout=10.0
    )

    firms = response.json() if response.status_code == 200 else []

except httpx.RequestError:
    firms = []
    st.error("Could not load firms.")


if firms:

    options = {
        f"{firm['id']} - {firm['name']}": firm["id"]
        for firm in firms
    }

    selected = st.selectbox(
        "Choose a firm",
        list(options.keys())
    )

    firm_id = options[selected]

    if st.button("Generate Summary"):

        output = st.empty()
        full_text = ""

        try:
            with httpx.stream(
                "GET",
                f"{API_BASE}/firms/{firm_id}/summary/stream",
                timeout=60.0,
            ) as response:

                if response.status_code == 200:

                    for chunk in response.iter_text():
                        full_text += chunk
                        output.markdown(full_text)

                elif response.status_code == 404:
                    st.error("Firm not found.")

                else:
                    st.error(
                        f"Streaming failed: HTTP {response.status_code}"
                    )

        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")