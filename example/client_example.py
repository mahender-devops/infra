# Example Relevance Test Service client
#
# This client is a simple example of using the RTS
# to:
# 1. Run a similarity relevance test
# 2. Obtain the results
# 3. Report selected metric scores
#
# This example could serve as the foundation for an automated
# regresssion test

import json
import copy
import requests
import argparse
import sys
import time
import itertools


REQUEST_TEMPLATE = {
    "metadata": {
        "name": "example test"
    },
    "sinequa": {
        "url": None,
        "profile": None,
        "user": None,
        "pwd": None,
        "count": 20,
        "nthreads": 8
    },
    "tests": [
        {
            "name": "Production Similarity",
            "queryset": None,
            "resultset": "rs_test.json",
            "scoring": [
                {
                    "type": "similarity",
                    "scorefile": "score_similarity.json",
                    "baseline": None,
                    "include_summary": True               
                }
            ]            
        }
    ]
}

SPINNER = itertools.cycle(['-', '/', '|', '\\'])


if __name__ == '__main__': 

    parser = argparse.ArgumentParser()
    parser.add_argument('--rtsurl', type=str, required=True, help='RTS REST endpoint')
    parser.add_argument('--queryset', type=str, required=True, help='S3 path to queryset')
    parser.add_argument('--baseline', type=str, required=True, help='S3 path to baseline resultset')
    parser.add_argument('--snprofile', type=str, required=True, help='Sinequa profile to use')
    parser.add_argument('--snurl', type=str, required=True, help='Sinequa REST endpoint URL')
    parser.add_argument('--user', type=str, required=True, help='Username for authentication')
    parser.add_argument('--pwd', type=str, required=True, help='Password for authentication')
    parser.add_argument('--domain', type=str, default=None, help='Domain for authentication')    
    parser.add_argument('--timeout', type=int, default=(5*60), help='Timeout in seconds')
    parser.add_argument('--polldelay', type=int, default=1, help='Polling delay in seconds')
    parser.add_argument('--nospinner', default=False, action='store_true', help='Dont show progress spinner')
    args = parser.parse_args()
    

    # Update request body based on arguments
    rqbody = copy.deepcopy(REQUEST_TEMPLATE)
    rqbody['sinequa']['url'] = args.snurl
    rqbody['sinequa']['profile'] = args.snprofile
    rqbody['sinequa']['user'] = args.user
    rqbody['sinequa']['pwd']  = args.pwd

    rqbody['tests'][0]['queryset'] = args.queryset
    rqbody['tests'][0]['scoring'][0]['baseline'] = args.baseline

    testScores = None    
    with requests.Session() as sess:

        # Make REST API call to submite request
        sub = sess.post(args.rtsurl+'/api/start', json=rqbody)
        subBody = json.loads(sub.text)
        
        if ((sub.status_code != 200) or
            (not 'status' in subBody) or
            (subBody['status'] != 'submitted')):
                # Error occurred. Handle appropriately
                print('Error submitting test request')
                sys.exit(1)

        # Poll until status is failed or succeeded
        uid = subBody['uid']
        startTime = time.time()
        while True:

            elapsedTime = time.time() - startTime
            if elapsedTime > args.timeout:
                print('Error: test exceeded timeout')
                break

            try:
                statusResp = sess.get(args.rtsurl+'/api/status', params={'uid': uid})
            except Exception as e:
                # Unexpected error. The sess object should handle
                # most connectivity issues
                pass
                                
            statusBody = json.loads(statusResp.text)
            
            if statusResp.status_code != 200:
                # Error occurred. Handle appropriately
                print('Error getting test status')
                break

            elif statusBody['status'] == 'failed':
                # Error occurred. Handle appropriately
                print('Error, test failed')
                break

            elif statusBody['status'] == 'succeeded':
                # Test completed. Save response            
                testScores = statusBody['scores']
                break
                
            # Test still pending. Sleep and try again. Display a simple
            # spinner to show that script is still alive
            if not args.nospinner:
                sys.stdout.write(next(SPINNER))
                sys.stdout.flush()            
                sys.stdout.write('\b')
            time.sleep(args.polldelay)

    if testScores != None:
        # Test succeeded. Report metric of interest.
        #
        # In this case, mean Jaccard similarity among
        # the first 20 rank positions
        score = testScores['Production Similarity'][0]['summary']['20']['ALL']['jaccard']['mean']
        print('similarity: {}'.format(score))
                
