from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
from sklearn.pipeline import Pipeline
import remembrall_util
import os

config_dict = remembrall_util.get_configs()
print config_dict
class MessageClassifier(object):

    def __init__(self):
        self.combined_training_data = list()
        self.classifier_pipeline = None


    def create_traning_data(self, file_path, label):
        training_list = list()
        try:
            with open(os.path.join(config_dict['PARENT_DIR'], file_path)) as f:
                for line in f:
                    line_dict = {'text': line.strip(), 'class': label}
                    training_list.append(line_dict)
        except Exception as err:
            print str(err)
            raise SystemExit
            #TODO: handle this
        return training_list

    def fetch_training_data(self):
        self.combined_training_data.extend(self.create_traning_data(config_dict['insult_training_data_file'], 'I'))
        self.combined_training_data.extend(self.create_traning_data(config_dict['compliment_training_data_file'], 'C'))
        self.combined_training_data.extend(self.create_traning_data(config_dict['question_training_data_file'], 'Q'))
        self.combined_training_data.extend(self.create_traning_data(config_dict['answer_training_data_file'], 'A'))

    def interpret_probabilites(self, prediction_dict, probabilities):
        print prediction_dict
        max_probability = max(probabilities)
        if max_probability == prediction_dict['A']:
            return 'A'
        elif max_probability == prediction_dict['Q']:
            return 'Q'
        elif max_probability > 0.76 and prediction_dict['I'] == max_probability:
            return 'I'
        elif max_probability > 0.76 and prediction_dict['C'] == max_probability:
            return 'C'
        else:
            if prediction_dict['A'] > prediction_dict['Q']:
                return 'A'
            else:
                return 'Q'

    def train_classifier(self):
        cls.fetch_training_data()
        training_df = DataFrame(self.combined_training_data)
        self.classifier_pipeline = Pipeline([('vectorizer', CountVectorizer()),
                                      ('classifier', MultinomialNB()) ])
        self.classifier_pipeline.fit(training_df['text'].values,
                                     training_df['class'].values)
        joblib.dump(self.classifier_pipeline, os.path.join(
            config_dict['PARENT_DIR'], config_dict['model_file_path']))

    def predict_message_type(self, text):
        try:
            self.classifier_pipeline = joblib.load(os.path.join(
                config_dict['PARENT_DIR'], config_dict['model_file_path']))
        except Exception as err:
            self.train_classifier()

        probabilities = self.classifier_pipeline.predict_proba(
            [text])[0].tolist()

        if text[-1] == "?":
             probabilities[-1] = probabilities[-1] + 0.4
        else:
            probabilities[0] += 0.35

        prediction_dict = {'A': probabilities[0], 'C': probabilities[1],
                           'I': probabilities[2], 'Q': probabilities[3]}
        prediction = self.interpret_probabilites(prediction_dict, probabilities)
        print "Final Prediction", prediction
        return prediction


if __name__ == '__main__':
    cls = MessageClassifier()
    #cls.train_classifier()
    cls.predict_message_type("test sentence here")