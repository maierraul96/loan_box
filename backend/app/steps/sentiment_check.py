from typing import Dict, Any
import os
from app.steps.base import BaseStep, StepResult

# OpenAI import with error handling
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SentimentCheck(BaseStep):
    """
    Sentiment Check Step (Agent-Style)

    Uses OpenAI API to analyze the loan_purpose text for risky or speculative keywords.
    Returns a risk score (0-100) that can be used by terminal rules.

    Requirements:
    - Set OPENAI_API_KEY environment variable
    - Install openai package: pip install openai

    Default risky terms: gambling, crypto, betting, casino, speculation, bitcoin,
    cryptocurrency, forex, day trading, stocks speculation

    Additional terms can be configured via step params.
    """

    step_type = "sentiment_check"

    # Extended default risky keywords list
    DEFAULT_RISKY_TERMS = [
        "gambling", "crypto", "betting", "casino", "speculation",
        "bitcoin", "cryptocurrency", "forex", "day trading",
        "stocks speculation", "lottery", "poker", "roulette",
        "slot machines", "sports betting", "ponzi", "pyramid scheme"
    ]

    def execute(self, application: Dict[str, Any], params: Dict[str, Any]) -> StepResult:
        """
        Analyze loan purpose for risky sentiment using OpenAI.

        Returns:
            StepResult with:
            - passed: Always True (risk score used by terminal rules instead)
            - computed_values: Contains risk_score (0-100), detected_risks, confidence
            - message: Description of analysis result
        """
        # Get parameters
        additional_terms = params.get("risky_terms", self.get_default_params()["risky_terms"])
        api_model = params.get("api_model", self.get_default_params()["api_model"])

        # Extract loan purpose
        loan_purpose = application.get("loan_purpose", "")

        # Combine default and additional risky terms
        all_risky_terms = self.DEFAULT_RISKY_TERMS + additional_terms

        # Perform sentiment analysis
        risk_score, detected_risks, confidence, analysis_method = self._analyze_sentiment(
            loan_purpose, all_risky_terms, api_model
        )

        # Create message
        if risk_score >= 70:
            risk_level = "HIGH RISK"
        elif risk_score >= 40:
            risk_level = "MODERATE RISK"
        else:
            risk_level = "LOW RISK"

        message = (
            f"Sentiment Analysis: {risk_level} (score: {risk_score}/100) - "
            f"Loan purpose: '{loan_purpose}' - "
            f"Method: {analysis_method}"
        )

        if detected_risks:
            message += f" - Detected: {', '.join(detected_risks)}"

        # Always pass - let terminal rules evaluate the risk_score
        return StepResult(
            passed=True,
            computed_values={
                "risk_score": risk_score,
                "detected_risks": detected_risks,
                "confidence": confidence,
                "loan_purpose": loan_purpose,
                "analysis_method": analysis_method
            },
            message=message
        )

    def _analyze_sentiment(
        self,
        loan_purpose: str,
        risky_terms: list,
        api_model: str
    ) -> tuple[int, list, float, str]:
        """
        Analyze sentiment using OpenAI API with fallback to keyword matching.

        Returns:
            (risk_score, detected_risks, confidence, analysis_method)
        """
        # Check if loan purpose is empty
        if not loan_purpose or not loan_purpose.strip():
            return 0, [], 1.0, "empty_purpose"

        # Try OpenAI API first
        api_key = os.environ.get("OPENAI_API_KEY")

        if OPENAI_AVAILABLE and api_key:
            try:
                return self._analyze_with_openai(loan_purpose, risky_terms, api_model)
            except Exception as e:
                # Log error and fall back to keyword matching
                print(f"OpenAI API error: {e}. Falling back to keyword matching.")

        # Fallback: Simple keyword matching
        return self._analyze_with_keywords(loan_purpose, risky_terms)

    def _analyze_with_openai(
        self,
        loan_purpose: str,
        risky_terms: list,
        api_model: str
    ) -> tuple[int, list, float, str]:
        """
        Use OpenAI API to analyze sentiment with AI understanding.
        """
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        # Construct prompt for sentiment analysis
        risky_terms_str = ", ".join(risky_terms)
        prompt = f"""Analyze the following loan purpose for risky or speculative intent.

Loan purpose: "{loan_purpose}"

Risky/speculative keywords to watch for: {risky_terms_str}

Please provide:
1. A risk score from 0-100 (0=completely safe, 100=extremely risky/speculative)
2. List any detected risky terms or concerns
3. Your confidence level (0.0-1.0)

Respond in this exact JSON format:
{{
  "risk_score": <number 0-100>,
  "detected_risks": [<list of strings>],
  "confidence": <number 0.0-1.0>
}}"""

        # Make API call
        # Note: gpt-5-mini supports default temperature=1, so we don't specify it
        response = client.chat.completions.create(
            model=api_model,
            messages=[
                {"role": "system", "content": "You are a financial risk analyst specializing in detecting risky or speculative loan purposes."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=25000  # High limit to ensure comprehensive risk analysis
        )

        # Parse response
        import json
        content = response.choices[0].message.content.strip()

        # Try to extract JSON from response
        try:
            # Handle case where response might have markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            result = json.loads(content)
            risk_score = int(result.get("risk_score", 50))
            detected_risks = result.get("detected_risks", [])
            confidence = float(result.get("confidence", 0.8))

            return risk_score, detected_risks, confidence, "openai_api"
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Failed to parse OpenAI response: {e}. Response: {content}")
            # Fall back to keyword matching
            return self._analyze_with_keywords(loan_purpose, risky_terms)

    def _analyze_with_keywords(
        self,
        loan_purpose: str,
        risky_terms: list
    ) -> tuple[int, list, float, str]:
        """
        Fallback method: Simple keyword matching for risky terms.
        """
        loan_purpose_lower = loan_purpose.lower()
        detected_risks = []

        for term in risky_terms:
            if term.lower() in loan_purpose_lower:
                detected_risks.append(term)

        # Calculate risk score based on number of matches
        if detected_risks:
            # If any risky term found, assign high risk
            risk_score = min(100, 80 + len(detected_risks) * 5)
            confidence = 0.9
        else:
            # No risky terms found
            risk_score = 20  # Conservative: assign low but non-zero risk
            confidence = 0.7  # Lower confidence without AI analysis

        return risk_score, detected_risks, confidence, "keyword_matching"

    @classmethod
    def get_default_params(cls) -> Dict[str, Any]:
        """
        Default parameters for sentiment check.

        Returns:
            risky_terms: Additional terms to add to default list (default: empty)
            api_model: OpenAI model to use (default: gpt-5-mini)
        """
        return {
            "risky_terms": [],
            "api_model": "gpt-5-mini"
        }
