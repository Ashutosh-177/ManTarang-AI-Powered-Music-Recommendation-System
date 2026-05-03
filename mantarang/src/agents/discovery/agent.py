"""
Refactored Discovery Agent - Phase 4

Modularized Discovery Agent using extracted components:
- DiscoveryConfig for intent parameter management
- DiscoveryScorer for discovery-specific scoring
- DiscoveryFilter for filtering logic
- DiscoveryDiversity for diversity management

This refactored version reduces the agent from 1680 lines to ~400 lines
while maintaining all functionality through better separation of concerns.
"""

from typing import Dict, List, Any
import structlog

from ...models.agent_models import MusicRecommenderState, AgentConfig
from ...models.recommendation_models import TrackRecommendation
from ...services.api_service import APIService
from ...services.metadata_service import MetadataService
from ..base_agent import BaseAgent
from ..components.unified_candidate_generator import UnifiedCandidateGenerator
from ..components import QualityScorer

# Phase 4: Import new modular components
from .discovery_config import DiscoveryConfig
from .discovery_scorer import DiscoveryScorer
from .discovery_filter import DiscoveryFilter
from .discovery_diversity import DiscoveryDiversity

logger = structlog.get_logger(__name__)


class DiscoveryAgent(BaseAgent):
    """
    Refactored Discovery Agent with modular components.
    
    Phase 4: Dramatically simplified through component extraction:
    - Configuration management → DiscoveryConfig
    - Scoring logic → DiscoveryScorer  
    - Filtering logic → DiscoveryFilter
    - Diversity management → DiscoveryDiversity
    
    Responsibilities:
    - Multi-hop similarity exploration
    - Underground and hidden gem detection
    - Serendipitous discovery beyond mainstream music
    - Novelty-optimized recommendations
    
    Uses shared and specialized components:
    - UnifiedCandidateGenerator for candidate generation
    - QualityScorer for base quality assessment
    - DiscoveryScorer for discovery-specific scoring
    - DiscoveryFilter for discovery-specific filtering
    - DiscoveryDiversity for variety management
    """
    
    def __init__(
        self,
        config: AgentConfig,
        llm_client,
        api_service: APIService,
        metadata_service: MetadataService,
        rate_limiter=None,
        session_manager=None
    ):
        """
        Initialize refactored discovery agent with modular components.
        
        Args:
            config: Agent configuration
            llm_client: LLM client for reasoning
            api_service: Unified API service
            metadata_service: Unified metadata service
            rate_limiter: Rate limiter for LLM API calls
            session_manager: SessionManagerService for candidate pool persistence
        """
        super().__init__(
            config=config, 
            llm_client=llm_client, 
            api_service=api_service,
            metadata_service=metadata_service,
            rate_limiter=rate_limiter
        )
        
        # ChromaDB setup
        import chromadb
        import os
        try:
            chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "chroma_data")
            self.chroma_client = chromadb.PersistentClient(path=chroma_path)
            self.chroma_collection = self.chroma_client.get_or_create_collection("music_tracks")
            self.logger.info("Successfully connected to ChromaDB local dataset")
        except Exception as e:
            self.logger.warning(f"Could not connect to ChromaDB: {e}")
            self.chroma_collection = None

        # Phase 4: Initialize modular components
        self.discovery_config = DiscoveryConfig()
        self.discovery_scorer = DiscoveryScorer()
        self.discovery_filter = DiscoveryFilter()
        self.discovery_diversity = DiscoveryDiversity()
        
        # Shared components
        self.candidate_generator = UnifiedCandidateGenerator(api_service, session_manager)
        self.quality_scorer = QualityScorer()
        
        # Current parameters (will be set by configuration)
        self.current_params = self.discovery_config.base_config.copy()
        
        self.logger.info("Phase 4: Refactored DiscoveryAgent initialized with modular components")
    
    async def process(self, state: MusicRecommenderState) -> MusicRecommenderState:
        """
        Process discovery recommendations using modular components.
        
        Phase 4: Simplified discovery processing with clear component separation.
        """
        try:
            # Extract entities and intent analysis from state
            entities = getattr(state, 'entities', {})
            intent_analysis = getattr(state, 'intent_analysis', {})
            
            # 🔧 FIX: Check if this is a follow-up query - if so, skip generation
            is_followup = intent_analysis.get('is_followup', False)
            if is_followup:
                self.logger.info("🔄 Follow-up query detected - skipping discovery generation, letting judge agent use persisted pool")
                state.discovery_recommendations = []
                return state
            
            # Determine if we should generate a large pool for follow-ups
            should_generate_pool = getattr(state, 'should_generate_large_pool', False)
            
            # 🔧 FIX: If not set on state, check planning_strategy
            if not should_generate_pool:
                planning_strategy = getattr(state, 'planning_strategy', {})
                should_generate_pool = planning_strategy.get('generate_large_pool', False)
            
            # Phase 4: Generate discovery candidates
            candidates = await self._generate_discovery_candidates(
                entities, intent_analysis, should_generate_pool, state
            )
            
            # 🔍 DEBUG: Log candidate details after generation
            self.logger.info(f"🔍 POST-GENERATION CANDIDATES: {len(candidates)} total")
            if candidates:
                sample_candidates = candidates[:3]
                for i, candidate in enumerate(sample_candidates):
                    self.logger.info(
                        f"🔍 Candidate {i+1}: {candidate.get('artist', 'Unknown')} - {candidate.get('name', 'Unknown')} "
                        f"(listeners: {candidate.get('listeners', 0)}, source: {candidate.get('source', 'unknown')})"
                    )
            
            if not candidates:
                self.logger.warning("No discovery candidates generated")
                state.discovery_recommendations = []
                return state
            
            # Phase 4: Use DiscoveryScorer for scoring
            self.logger.info(f"🔍 PRE-SCORING: Sending {len(candidates)} candidates to DiscoveryScorer")
            scored_candidates = await self.discovery_scorer.score_discovery_candidates(
                candidates, entities, intent_analysis, self.quality_scorer
            )
            
            # 🔍 DEBUG: Log candidate details after scoring
            self.logger.info(f"🔍 POST-SCORING CANDIDATES: {len(scored_candidates)} total")
            if scored_candidates:
                sample_scored = scored_candidates[:3]
                for i, candidate in enumerate(sample_scored):
                    self.logger.info(
                        f"🔍 Scored {i+1}: {candidate.get('artist', 'Unknown')} - {candidate.get('name', 'Unknown')} "
                        f"(listeners: {candidate.get('listeners', 0)}, quality: {candidate.get('quality_score', 0):.3f})"
                    )
            
            # Phase 4: Use DiscoveryFilter for filtering
            self.logger.info(f"🔍 PRE-FILTERING: Sending {len(scored_candidates)} candidates to DiscoveryFilter")
            filtered_candidates = await self.discovery_filter.filter_for_discovery(
                scored_candidates,
                entities,
                intent_analysis,
                self.current_params.get('quality_threshold', 0.3),
                self.current_params.get('novelty_threshold', 0.4)
            )
            
            # 🔍 DEBUG: Log candidate details after filtering
            self.logger.info(f"🔍 POST-FILTERING CANDIDATES: {len(filtered_candidates)} total")
            if filtered_candidates:
                sample_filtered = filtered_candidates[:3]
                for i, candidate in enumerate(sample_filtered):
                    self.logger.info(
                        f"🔍 Filtered {i+1}: {candidate.get('artist', 'Unknown')} - {candidate.get('name', 'Unknown')} "
                        f"(listeners: {candidate.get('listeners', 0)}, combined_score: {candidate.get('combined_score', 0):.3f})"
                    )
            
            # Phase 4: Use DiscoveryDiversity for diversity management
            self.logger.info(f"🔍 PRE-DIVERSITY: Sending {len(filtered_candidates)} candidates to DiscoveryDiversity")
            diverse_candidates = self.discovery_diversity.ensure_discovery_diversity(
                filtered_candidates, intent_analysis
            )
            
            # 🔍 DEBUG: Log candidate details after diversity
            self.logger.info(f"🔍 POST-DIVERSITY CANDIDATES: {len(diverse_candidates)} total")
            if diverse_candidates:
                sample_diverse = diverse_candidates[:3]
                for i, candidate in enumerate(sample_diverse):
                    self.logger.info(
                        f"🔍 Diverse {i+1}: {candidate.get('artist', 'Unknown')} - {candidate.get('name', 'Unknown')} "
                        f"(listeners: {candidate.get('listeners', 0)}, source: {candidate.get('source', 'unknown')})"
                    )
            
            # Create final recommendations
            self.logger.info(f"🔍 PRE-RECOMMENDATION: Creating recommendations from {len(diverse_candidates)} candidates")
            recommendations = await self._create_discovery_recommendations(
                diverse_candidates, entities, intent_analysis
            )
            
            # 🔍 DEBUG: Log final recommendations
            self.logger.info(f"🔍 FINAL RECOMMENDATIONS: {len(recommendations)} total")
            if recommendations:
                sample_final = recommendations[:3]
                for i, rec in enumerate(sample_final):
                    listeners = getattr(rec, 'additional_scores', {}).get('listeners', 0)
                    self.logger.info(
                        f"🔍 Final {i+1}: {rec.artist} - {rec.title} "
                        f"(listeners: {listeners}, confidence: {rec.confidence:.3f})"
                    )
            
            state.discovery_recommendations = recommendations
            self.logger.info(f"Phase 4: Generated {len(recommendations)} discovery recommendations")
            
            return state
            
        except Exception as e:
            self.logger.error(f"Discovery processing failed: {e}")
            state.discovery_recommendations = []
            return state
    
    async def _generate_discovery_candidates(
        self,
        entities: Dict[str, Any],
        intent_analysis: Dict[str, Any],
        should_generate_pool: bool = False,
        state: MusicRecommenderState = None
    ) -> List[Dict[str, Any]]:
        """
        Generate discovery candidates using UnifiedCandidateGenerator.
        
        Phase 4: Simplified candidate generation using shared component.
        """
        try:
            # Get candidate focus strategy from configuration
            # Fix: Use the actual detected intent from query understanding, not default to 'discovery'
            detected_intent = intent_analysis.get('intent')
            if not detected_intent:
                # Try to get from query_understanding in intent_analysis
                query_understanding = intent_analysis.get('query_understanding')
                if query_understanding and hasattr(query_understanding, 'intent'):
                    detected_intent = query_understanding.intent.value if hasattr(query_understanding.intent, 'value') else str(query_understanding.intent)
                else:
                    detected_intent = 'discovery'  # Final fallback
            
            self.logger.info(f"🎯 DISCOVERY AGENT: Using detected intent: {detected_intent}")
            self.logger.info(f"🔍 DEBUG intent_analysis: {intent_analysis}")
            
            # Get session_id from state if available (needed for pool generation)
            session_id = getattr(state, 'session_id', None) or 'default_session'
            
            # Custom Dataset Query Check
            if self.chroma_collection is not None and (detected_intent in ['artist_similarity', 'discovery'] or True): # Enabled for all discovery
                artist_name = entities.get('artist', "music")
                if not isinstance(artist_name, str):
                   artist_name = str(artist_name)
                self.logger.info(f"Querying local ChromaDB for: {artist_name}")
                
                try:
                    results = self.chroma_collection.query(
                        query_texts=[artist_name],
                        n_results=10
                    )
                    
                    local_candidates = []
                    if results and results.get('metadatas') and results['metadatas'][0]:
                        for idx, meta in enumerate(results['metadatas'][0]):
                            candidate = {
                                'artist': meta.get('artist', 'Unknown Artist'),
                                'name': meta.get('title', 'Unknown Track'),
                                'source': 'local_csv_dataset',
                                'popularity': meta.get('popularity', 0),
                                'genres': meta.get('genres', '').split(',') if meta.get('genres') else [],
                                'url': '',
                                'listeners': meta.get('popularity', 0) * 1000,
                            }
                            local_candidates.append(candidate)
                        
                        if local_candidates:
                            self.logger.info(f"Found {len(local_candidates)} local candidates from CSV dataset")
                            return local_candidates
                except Exception as e:
                    self.logger.warning(f"Chroma DB generation Failed: {e}")

            # Phase 3: Generate large pool if recommended by PlannerAgent
            if should_generate_pool:
                self.logger.info("Phase 3: Generating large candidate pool for future follow-ups")
                pool_key = await self.candidate_generator.generate_and_persist_large_pool(
                    entities=entities,
                    intent_analysis=intent_analysis,
                    session_id=session_id,
                    agent_type="discovery",
                    detected_intent=detected_intent
                )
                if pool_key:
                    self.logger.info(f"Large pool generated with key: {pool_key}")
                
                # Fall back to standard generation if pool generation fails
                candidates = await self.candidate_generator.generate_candidate_pool(
                    entities=entities,
                    intent_analysis=intent_analysis,
                    agent_type="discovery",
                    target_candidates=self.current_params.get('target_candidates', 200),
                    detected_intent=detected_intent,
                    recently_shown_track_ids=getattr(self, '_recently_shown_track_ids', [])
                )
            else:
                # Standard candidate generation
                candidates = await self.candidate_generator.generate_candidate_pool(
                    entities=entities,
                    intent_analysis=intent_analysis,
                    agent_type="discovery",
                    target_candidates=self.current_params.get('target_candidates', 200),
                    detected_intent=detected_intent,
                    recently_shown_track_ids=getattr(self, '_recently_shown_track_ids', [])
                )
            
            self.logger.info(f"Generated {len(candidates)} discovery candidates")
            return candidates
            
        except Exception as e:
            self.logger.error(f"Candidate generation failed: {e}")
            return []
    
    async def _create_discovery_recommendations(
        self,
        candidates: List[Dict[str, Any]],
        entities: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> List[TrackRecommendation]:
        """
        Create final discovery recommendations from candidates.
        
        Phase 4: Simplified recommendation creation focusing on core logic.
        """
        recommendations = []
        final_count = self.current_params.get('final_recommendations', 20)
        
        # Get candidates to process
        candidates_to_process = candidates[:final_count]
        
        # Generate reasoning for all candidates in a single batch call
        reasoning_list = await self._generate_batch_discovery_reasoning(
            candidates_to_process, entities, intent_analysis
        )
        
        for i, candidate in enumerate(candidates_to_process):
            try:
                # Get reasoning from batch results or use fallback
                reasoning = reasoning_list[i] if i < len(reasoning_list) else self._create_discovery_fallback_reasoning(
                    candidate, entities, intent_analysis, i + 1
                )
                
                # Create TrackRecommendation
                recommendation = TrackRecommendation(
                    title=candidate.get('name', 'Unknown Track'),
                    artist=candidate.get('artist', 'Unknown Artist'),
                    id=f"{candidate.get('artist', 'Unknown')}_{candidate.get('name', 'Unknown')}_{i}",
                    source='discovery_agent',
                    track_url=candidate.get('url', ''),
                    explanation=reasoning,
                    confidence=candidate.get('combined_score', 0.5),
                    genres=candidate.get('genres', []),
                    novelty_score=candidate.get('novelty_score', 0),
                    quality_score=candidate.get('quality_score', 0),
                    additional_scores={
                        'underground_score': candidate.get('underground_score', 0),
                        'similarity_score': candidate.get('similarity_score', 0),
                        'discovery_score': candidate.get('discovery_score', 0),
                        'listeners': candidate.get('listeners', 0),
                        'tags': candidate.get('tags', [])
                    }
                )
                
                recommendations.append(recommendation)
                
            except Exception as e:
                self.logger.warning(f"Failed to create recommendation for candidate {i}: {e}")
                continue
        
        return recommendations

    async def _generate_batch_discovery_reasoning(
        self,
        candidates: List[Dict[str, Any]],
        entities: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Generate reasoning for multiple discovery recommendations in a single LLM call.
        
        This avoids rate limiting issues by batching all reasoning generation.
        """
        try:
            if not candidates:
                return []
            
            # Build batch prompt for all candidates
            batch_prompt = self._build_batch_reasoning_prompt(candidates, entities, intent_analysis)
            
            # Make single LLM call for all reasoning
            response = await self.llm_utils.call_llm(batch_prompt)
            
            # Parse response into individual reasoning strings
            reasoning_list = self._parse_batch_reasoning_response(response, len(candidates))
            
            self.logger.info(f"Generated batch reasoning for {len(reasoning_list)} recommendations")
            return reasoning_list
            
        except Exception as e:
            self.logger.warning(f"Batch reasoning generation failed: {e}")
            # Return fallback reasoning for all candidates
            return [
                self._create_discovery_fallback_reasoning(candidate, entities, intent_analysis, i + 1)
                for i, candidate in enumerate(candidates)
            ]

    def _build_batch_reasoning_prompt(
        self,
        candidates: List[Dict[str, Any]],
        entities: Dict[str, Any],
        intent_analysis: Dict[str, Any]
    ) -> str:
        """
        Build a prompt for generating reasoning for multiple recommendations in batch.
        """
        intent = intent_analysis.get('intent', 'discovery')
        
        prompt_parts = [
            "Generate brief, engaging explanations for why each of these tracks is recommended for music discovery.",
            f"User Intent: {intent}",
            "",
            "For each track, provide a concise 1-2 sentence explanation focusing on what makes it special for discovery.",
            "",
            "Tracks to explain:"
        ]
        
        # Add each candidate with its details
        for i, candidate in enumerate(candidates, 1):
            artist = candidate.get('artist', 'Unknown')
            track = candidate.get('name', 'Unknown')
            genres = candidate.get('genres', [])
            novelty_score = candidate.get('novelty_score', 0)
            underground_score = candidate.get('underground_score', 0)
            quality_score = candidate.get('quality_score', 0)
            
            prompt_parts.extend([
                f"{i}. {track} by {artist}",
                f"   Genres: {', '.join(genres[:3]) if genres else 'Various'}",
                f"   Novelty: {novelty_score:.2f}, Underground: {underground_score:.2f}, Quality: {quality_score:.2f}",
                ""
            ])
        
        prompt_parts.extend([
            "Format your response as a numbered list:",
            "1. [Explanation for first track]",
            "2. [Explanation for second track]",
            "...",
            "",
            "Keep each explanation concise and engaging. Focus on discovery appeal."
        ])
        
        return "\n".join(prompt_parts)

    def _parse_batch_reasoning_response(self, response: str, expected_count: int) -> List[str]:
        """
        Parse the batch reasoning response into individual explanations.
        """
        try:
            lines = response.strip().split('\n')
            reasoning_list = []
            
            current_reasoning = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check if line starts with a number (e.g., "1.", "2.", etc.)
                import re
                if re.match(r'^\d+\.', line):
                    # Save previous reasoning if we have one
                    if current_reasoning:
                        reasoning_list.append(current_reasoning.strip())
                    
                    # Start new reasoning (remove the number prefix)
                    current_reasoning = re.sub(r'^\d+\.\s*', '', line)
                else:
                    # Continue current reasoning
                    if current_reasoning:
                        current_reasoning += " " + line
                    else:
                        current_reasoning = line
            
            # Add the last reasoning
            if current_reasoning:
                reasoning_list.append(current_reasoning.strip())
            
            # Ensure we have enough reasoning entries
            while len(reasoning_list) < expected_count:
                reasoning_list.append("An interesting discovery worth exploring.")
            
            # Truncate if we have too many
            return reasoning_list[:expected_count]
            
        except Exception as e:
            self.logger.warning(f"Failed to parse batch reasoning response: {e}")
            # Return fallback reasoning
            return ["An interesting discovery worth exploring."] * expected_count
    
    def _create_discovery_fallback_reasoning(
        self,
        candidate: Dict[str, Any],
        entities: Dict[str, Any],
        intent_analysis: Dict[str, Any],
        rank: int
    ) -> str:
        """
        Create fallback reasoning when LLM generation fails.
        
        Phase 4: Simplified fallback reasoning based on scores.
        """
        artist = candidate.get('artist', 'Unknown Artist')
        track = candidate.get('name', 'Unknown Track')
        
        # Determine primary appeal based on scores
        novelty_score = candidate.get('novelty_score', 0)
        underground_score = candidate.get('underground_score', 0)
        quality_score = candidate.get('quality_score', 0)
        
        if underground_score > 0.6:
            appeal = "underground gem"
        elif novelty_score > 0.5:
            appeal = "novel discovery"
        elif quality_score > 0.7:
            appeal = "high-quality track"
        else:
            appeal = "interesting find"
        
        # Get genre context
        genres = candidate.get('genres', [])
        genre_text = f" in {genres[0]}" if genres else ""
        
        return f"'{track}' by {artist} is an {appeal}{genre_text} worth exploring."
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current discovery parameters for debugging/monitoring."""
        return self.current_params.copy()
    
    def update_parameters(self, new_params: Dict[str, Any]) -> None:
        """Update discovery parameters (for testing/debugging)."""
        validated_params = self.discovery_config.validate_parameters(new_params)
        self.current_params.update(validated_params)
        self.logger.info("Discovery parameters updated", new_params=validated_params) 