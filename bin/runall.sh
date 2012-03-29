SIZE=1000
ITERATIONS=10000

PYTHONPATH=.:$PYTHONPATH
FILENAME="benches_${SIZE}_${ITERATIONS}.txt"
CURRENT_COMMIT=`git log -n 1 --format=format:"%H"`
BASE_DIR="../pynetsym_stats"

echo "REGULAR RUN"
echo "NX RND \c" 
python pynetsym/generation_models/transitive_linking.py -n ${SIZE} -s ${ITERATIONS} 
if [[ "$?x" != 0x ]]; then
    echo Execution failed
    exit 1
fi
echo "NX PA  \c" 
python pynetsym/generation_models/transitive_linking.py -n ${SIZE} -s ${ITERATIONS} --preferential-attachment 
echo "IG RND \c" 
python pynetsym/generation_models/transitive_linking_igraph.py -n ${SIZE} -s ${ITERATIONS} 
echo "IG PA  \c" 
python pynetsym/generation_models/transitive_linking_igraph.py -n ${SIZE} -s ${ITERATIONS} --preferential-attachment 

