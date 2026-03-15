import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from services.sentence_splitter import SentenceSplitter

def test_sentence_splitter():
    splitter = SentenceSplitter()
    results = []
    
    # Simulate streaming tokens
    for token in ["Chào ", "bạn. ", "Hôm ", "nay ", "thế ", "nào?"]:
        sentence = splitter.append_token(token)
        if sentence:
            results.append(sentence)
    
    # Remaining
    last = splitter.get_remaining()
    if last:
        results.append(last)
        
    assert results == ["Chào bạn.", "Hôm nay thế nào?"]

def test_sentence_splitter_with_exclamation():
    splitter = SentenceSplitter()
    results = []
    
    for token in ["Tuyệt ", "vời! ", "Cảm ", "ơn."]:
        sentence = splitter.append_token(token)
        if sentence:
            results.append(sentence)
    
    last = splitter.get_remaining()
    if last:
        results.append(last)
        
    assert results == ["Tuyệt vời!", "Cảm ơn."]
