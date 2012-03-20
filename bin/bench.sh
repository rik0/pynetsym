SIZE=1000
ITERATIONS=10000

PYTHONPATH=.:$PYTHONPATH
FILENAME="benches_${SIZE}_${ITERATIONS}.txt"
CURRENT_COMMIT=`git log -n 1 --format=format:"%H"`
BASE_DIR="../pynetsym_stats"

echo "REGULAR RUN"
echo "NX RND \c" >> $FILENAME
python pynetsym/generation_models/transitive_linking.py -n ${SIZE} -s ${ITERATIONS} >> $FILENAME
echo "NX PA  \c" >> $FILENAME
python pynetsym/generation_models/transitive_linking.py -n ${SIZE} -s ${ITERATIONS} --preferential-attachment >> $FILENAME
echo "IG RND \c" >> $FILENAME
python pynetsym/generation_models/transitive_linking_igraph.py -n ${SIZE} -s ${ITERATIONS} >> $FILENAME
echo "IG PA  \c" >> $FILENAME
python pynetsym/generation_models/transitive_linking_igraph.py -n ${SIZE} -s ${ITERATIONS} --preferential-attachment >> $FILENAME

echo "PROFILED RUN"
time python -mcProfile -o tl_nx_${SIZE}_${ITERATIONS}.stats pynetsym/generation_models/transitive_linking.py -n $SIZE -s ${ITERATIONS}
time python -mcProfile -o tl_nx_pa_${SIZE}_${ITERATIONS}.stats pynetsym/generation_models/transitive_linking.py -n $SIZE -s ${ITERATIONS} --preferential-attachment
time python -mcProfile -o tl_igraph_${SIZE}_${ITERATIONS}.stats pynetsym/generation_models/transitive_linking_igraph.py -n $SIZE -s ${ITERATIONS}
time python -mcProfile -o tl_igraph_pa_${SIZE}_${ITERATIONS}.stats pynetsym/generation_models/transitive_linking_igraph.py -n $SIZE -s ${ITERATIONS} --preferential-attachment

FULL_DIR="$BASE_DIR/$CURRENT_COMMIT"
echo "MOVING TO ${FULL_DIR}."
mkdir -p $FULL_DIR
mv *.stats $FULL_DIR
mv $FILENAME $FULL_DIR
ln -s $FULL_DIR ${BASE_DIR}/Current
